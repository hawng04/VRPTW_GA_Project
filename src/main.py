import os
import random
random.seed(42)
import time
from dataloader import SolomonDataLoader
from individual import Individual
from ga_operators import (
    tournament_selection, 
    order_crossover, 
    swap_mutation, 
    inversion_mutation, 
    relocate_mutation, 
    ruin_and_recreate_mutation,
    two_opt_mutation
)
from utils import plot_routes

# --- THIẾT LẬP THAM SỐ THỰC NGHIỆM ---
POP_SIZE = 200          # Kích thước quần thể
MAX_GEN = 1000           # Số thế hệ tối đa
CROSSOVER_RATE = 0.7   # Tỷ lệ lai ghép
MUTATION_RATE = 0.9     # Tỷ lệ đột biến cao để kích hoạt Ruin & Recreate
ELITISM_RATE = 0.05     # Tỷ lệ giữ lại tinh hoa

def pfih_initialization(data_loader):
    """
    Khởi tạo PFIH (Push Forward Insertion Heuristic) - Chuẩn 6 bước Chương 2
    Chèn ép khách hàng vào mọi vị trí khả thi để tối ưu số xe.
    """
    unrouted = set(range(1, len(data_loader.customers) + 1))
    chromosome = []

    while unrouted:
        route = []
        # Bước 1: Chọn Hạt giống - Khách hàng có giờ đóng cửa khắt khe nhất để giao trước
        seed_cust = min(unrouted, key=lambda c: data_loader.customers[c-1]['due_date'])
        route.append(seed_cust)
        unrouted.remove(seed_cust)
        
        while unrouted:
            best_cust = None
            best_pos = -1
            best_cost = float('inf')
            
            # Bước 2 & 3: Tính chi phí chèn và kiểm tra Push-forward
            for cust_idx in unrouted:
                cust_data = data_loader.customers[cust_idx - 1]
                
                # Thử chèn vào mọi khe hở trong tuyến đường hiện tại
                for pos in range(len(route) + 1):
                    temp_route = route[:pos] + [cust_idx] + route[pos:]
                    
                    is_feasible = True
                    temp_load = 0.0
                    current_time = 0.0
                    prev_node = 0
                    
                    # Mô phỏng xe chạy để kiểm tra Ràng buộc
                    for node in temp_route:
                        n_data = data_loader.customers[node - 1]
                        temp_load += n_data['demand']
                        if temp_load > data_loader.vehicle_capacity:
                            is_feasible = False
                            break # Vượt tải
                        
                        dist = data_loader.distance_matrix[prev_node][node]
                        arrival = current_time + dist
                        if arrival > n_data['due_date']:
                            is_feasible = False
                            break # Trễ giờ
                        
                        start_service = max(arrival, n_data['ready_time'])
                        current_time = start_service + n_data['service_time']
                        prev_node = node
                    
                    if is_feasible:
                        # Bước 4: Tính chi phí gia tăng
                        if pos == 0:
                            dist_inc = data_loader.distance_matrix[0][cust_idx] + data_loader.distance_matrix[cust_idx][route[0]] - data_loader.distance_matrix[0][route[0]]
                        elif pos == len(route):
                            dist_inc = data_loader.distance_matrix[route[-1]][cust_idx] + data_loader.distance_matrix[cust_idx][0] - data_loader.distance_matrix[route[-1]][0]
                        else:
                            dist_inc = data_loader.distance_matrix[route[pos-1]][cust_idx] + data_loader.distance_matrix[cust_idx][route[pos]] - data_loader.distance_matrix[route[pos-1]][route[pos]]
                        
                        if dist_inc < best_cost:
                            best_cost = dist_inc
                            best_cust = cust_idx
                            best_pos = pos
                            
            # Bước 5: Chèn và cập nhật
            if best_cust is not None:
                route.insert(best_pos, best_cust)
                unrouted.remove(best_cust)
            else:
                break # Bước 6: Không ai hợp lệ nữa -> Đóng xe
                
        chromosome.extend(route)
    return chromosome

def create_initial_population(data_loader):
    """ Khởi tạo quần thể với 20% PFIH và 80% Ngẫu nhiên """
    population = []
    num_customers = len(data_loader.customers)
    base_chromosome = list(range(1, num_customers + 1))
    
    num_pfih = int(POP_SIZE * 0.20)
    pfih_chrom = pfih_initialization(data_loader) 
    
    for _ in range(num_pfih):
        mutated_pfih = swap_mutation(pfih_chrom) 
        ind = Individual(mutated_pfih, data_loader)
        ind.evaluate_fitness()
        population.append(ind)
        
    for _ in range(POP_SIZE - num_pfih):
        chrom = base_chromosome.copy()
        random.shuffle(chrom)
        ind = Individual(chrom, data_loader)
        ind.evaluate_fitness()
        population.append(ind)
        
    return population

def run_genetic_algorithm(data_loader):
    """Chu trình hoạt động của GA (Mục 2.3.6)"""
    print(f"\n🚀 Đang khởi tạo quần thể ban đầu ({POP_SIZE} cá thể)...")
    population = create_initial_population(data_loader)
    
    best_individual = max(population, key=lambda ind: ind.fitness)
    print(f"🌟 Chi phí ban đầu (Gen 0 - PFIH): {best_individual.z_cost:.2f} | Số xe: {len(best_individual.routes)}")

    num_elites = int(POP_SIZE * ELITISM_RATE)
    
    for gen in range(1, MAX_GEN + 1):
        new_population = []
        
        population.sort(key=lambda ind: ind.fitness, reverse=True)
        new_population.extend(population[:num_elites])
        
        while len(new_population) < POP_SIZE:
            parent1 = tournament_selection(population)
            parent2 = tournament_selection(population)
            
            if random.random() < CROSSOVER_RATE:
                child_chrom = order_crossover(parent1.chromosome, parent2.chromosome)
            else:
                child_chrom = parent1.chromosome.copy()
                
            # Phép Đột biến Metaheuristic (5 Vũ khí)
            if random.random() < MUTATION_RATE:
                mut_type = random.random()
                if mut_type < 0.15:
                    child_chrom = swap_mutation(child_chrom)
                elif mut_type < 0.30:
                    child_chrom = relocate_mutation(child_chrom)
                elif mut_type < 0.50:
                    # 20% tung chiêu gỡ chéo đường (truyền parent1 đã giải mã tuyến)
                    child_chrom = two_opt_mutation(parent1, data_loader)
                elif mut_type < 0.70:
                    # 20% tung chiêu đảo ngược diện rộng
                    child_chrom = inversion_mutation(child_chrom)
                else:
                    # 30% tung chiêu đập xe thừa
                    child_chrom = ruin_and_recreate_mutation(parent1, data_loader)
                    
            child = Individual(child_chrom, data_loader)
            child.evaluate_fitness()
            new_population.append(child)
            
        population = new_population
        current_best = max(population, key=lambda ind: ind.fitness)
        
        if current_best.fitness > best_individual.fitness:
            best_individual = current_best
            print(f"🌟 [Kỷ lục mới] Thế hệ {gen}: Chi phí = {best_individual.z_cost:.2f} | Số xe = {len(best_individual.routes)}")
            
        elif gen % 100 == 0:
            print(f"⏳ Đang chạy... Thế hệ {gen}/{MAX_GEN}")

    return best_individual

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_dir = os.path.join(project_root, 'data')
    
    all_files = os.listdir(data_dir)
    datasets = []
    
    for f in all_files:
        f_lower = f.lower() 
   
        if f_lower.endswith('.txt') and f_lower.startswith('c2'):
            datasets.append(f)
            
    datasets.sort() 
    
    if not datasets:
        print("❌ Không tìm thấy file nào khớp với bộ lọc!")
        return

    group_stats = {}

    for filename in datasets:
        filepath = os.path.join(data_dir, filename)
        dataset_name = filename.replace('.txt', '').upper()
        
        loader = SolomonDataLoader(filepath)
        loader.load_data()
        
        start_time = time.time()
        best_solution = run_genetic_algorithm(loader)
        end_time = time.time()
        
        execution_time = end_time - start_time
        num_vehicles = len(best_solution.routes)
        total_dist = best_solution.total_distance
        
        # 1. In kết quả chi tiết của từng file
        print(f"{dataset_name:<12} | {num_vehicles:<15} | {total_dist:<20.2f} | {execution_time:<15.2f}")
        plot_routes(best_solution, loader, filename=f"map_{dataset_name}.png")

        # 2. Gom số liệu để tính trung bình
        # Gọt bỏ 2 ký tự cuối của tên file để lấy tên nhóm (VD: 'C101'[:-2] -> 'C1')
        group = dataset_name[:-2] 
        
        if group not in group_stats:
            group_stats[group] = {'vehicles': 0, 'distance': 0.0, 'time': 0.0, 'count': 0}
            
        group_stats[group]['vehicles'] += num_vehicles
        group_stats[group]['distance'] += total_dist
        group_stats[group]['time'] += execution_time
        group_stats[group]['count'] += 1

    print("-" * 68)
    
    # =====================================================================
    # IN BẢNG TỔNG HỢP TRUNG BÌNH (DÙNG ĐỂ SO SÁNH VỚI BÁO CÁO SOLOMON)
    # =====================================================================
    print("\n=========================================================================")
    print(" BẢNG TỔNG HỢP TRUNG BÌNH (AVERAGE) THEO NHÓM DỮ LIỆU ")
    print("=========================================================================")
    print(f"{'Nhóm':<10} | {'Số file':<10} | {'Số xe TB':<15} | {'Quãng đường TB':<20} | {'Time TB (s)':<15}")
    print("-" * 75)

    for grp, stats in sorted(group_stats.items()):
        count = stats['count']
        avg_veh = stats['vehicles'] / count
        avg_dist = stats['distance'] / count
        avg_time = stats['time'] / count
        
        print(f"{grp:<10} | {count:<10} | {avg_veh:<15.2f} | {avg_dist:<20.2f} | {avg_time:<15.2f}")

    print("-" * 75)
    print("✅ ĐÃ HOÀN TẤT CHẠY THỰC NGHIỆM VÀ XUẤT THỐNG KÊ!")

if __name__ == "__main__":
    main()