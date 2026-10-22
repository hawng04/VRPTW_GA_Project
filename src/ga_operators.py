import random

def tournament_selection(population, k=3):
    """Chọn lọc giải đấu (Tournament Selection)"""
    return max(random.sample(population, k), key=lambda ind: ind.fitness)

def order_crossover(parent1_chrom, parent2_chrom):
    """Toán tử lai ghép thứ tự (Order Crossover - OX)"""
    n = len(parent1_chrom)
    child_chrom = [-1] * n
    
    start, end = sorted(random.sample(range(n), 2))
    child_chrom[start:end+1] = parent1_chrom[start:end+1]
    
    p2_idx = (end + 1) % n
    c_idx = (end + 1) % n
    
    while -1 in child_chrom:
        if parent2_chrom[p2_idx] not in child_chrom:
            child_chrom[c_idx] = parent2_chrom[p2_idx]
            c_idx = (c_idx + 1) % n
        p2_idx = (p2_idx + 1) % n
        
    return child_chrom

def swap_mutation(chromosome):
    """Đột biến hoán đổi (Swap Mutation)"""
    mutated = chromosome.copy()
    idx1, idx2 = random.sample(range(len(mutated)), 2)
    mutated[idx1], mutated[idx2] = mutated[idx2], mutated[idx1]
    return mutated

def inversion_mutation(chromosome):
    """Đột biến đảo ngược (Inversion Mutation)"""
    mutated = chromosome.copy()
    start, end = sorted(random.sample(range(len(mutated)), 2))
    mutated[start:end+1] = reversed(mutated[start:end+1])
    return mutated

# =====================================================================
# CÁC TOÁN TỬ TỐI ƯU HÓA NÂNG CAO (LOCAL SEARCH & MEMETIC)
# =====================================================================

def relocate_mutation(chromosome):
    """Đột biến chèn ép (Relocate/Shift Mutation)"""
    mutated = chromosome.copy()
    cust = mutated.pop(random.randrange(len(mutated)))
    mutated.insert(random.randrange(len(mutated) + 1), cust)
    return mutated

def ruin_and_recreate_mutation(individual, data_loader):
    """
    Phép đột biến Hủy diệt & Sửa chữa (Ruin & Recreate)
    Hướng 3: Đập bỏ tuyến ít khách nhất, nhét họ vào cạnh những người hàng xóm gần nhất.
    """
    if len(individual.routes) <= 1:
        return individual.chromosome.copy()

    # 1. RUIN (Phá hủy): Chọn tuyến đường yếu nhất (chở ít khách nhất)
    smallest_route = min(individual.routes, key=len)
    
    new_chrom = individual.chromosome.copy()
    for cust in smallest_route:
        new_chrom.remove(cust)
        
    # 2. RECREATE (Sửa chữa thông minh): Nhét ép dựa vào khoảng cách địa lý
    for cust in smallest_route:
        best_neighbor = None
        best_dist = float('inf')
        
        for potential_neighbor in new_chrom:
            dist = data_loader.distance_matrix[cust][potential_neighbor]
            if dist < best_dist:
                best_dist = dist
                best_neighbor = potential_neighbor
                
        if best_neighbor is not None:
            neighbor_idx = new_chrom.index(best_neighbor)
            insert_pos = neighbor_idx if random.random() < 0.5 else neighbor_idx + 1
            new_chrom.insert(insert_pos, cust)
        else:
            new_chrom.append(cust)
            
    return new_chrom

def two_opt_mutation(individual, data_loader):
    """
    Đột biến Two-Opt (Intra-route Local Search)
    Mục tiêu: Gỡ rối các đường chéo nhau (hình chữ X) trong cùng 1 xe để giảm quãng đường.
    """
    if not individual.routes:
        return individual.chromosome.copy()
        
    new_chrom = individual.chromosome.copy()
    
    # Lọc ra các xe có từ 3 khách trở lên mới có thể bị chéo đường
    valid_routes = [r for r in individual.routes if len(r) >= 3]
    if not valid_routes:
        return new_chrom
        
    # Chọn ngẫu nhiên 1 xe để tối ưu
    route = random.choice(valid_routes)
    best_route = route.copy()
    
    # Hàm phụ: Tính tổng quãng đường của 1 xe
    def calc_route_dist(r):
        dist = data_loader.distance_matrix[0][r[0]]
        for i in range(len(r) - 1):
            dist += data_loader.distance_matrix[r[i]][r[i+1]]
        dist += data_loader.distance_matrix[r[-1]][0]
        return dist
        
    best_dist = calc_route_dist(route)
    
    # Quét Two-Opt: Thử đảo ngược mọi đoạn có thể trong xe này
    for i in range(len(route) - 1):
        for j in range(i + 1, len(route)):
            temp_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
            temp_dist = calc_route_dist(temp_route)
            
            # Nếu tìm thấy đường đi ngắn hơn -> Chốt luôn
            if temp_dist < best_dist:
                best_dist = temp_dist
                best_route = temp_route
                
    # Lắp ráp lại xe đã tối ưu vào chuỗi gen
    if best_route != route:
        start_idx = new_chrom.index(route[0])
        new_chrom[start_idx : start_idx + len(route)] = best_route
        
    return new_chrom