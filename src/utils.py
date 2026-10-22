import matplotlib.pyplot as plt
import numpy as np
import os

def plot_routes(best_solution, data_loader, filename="routes.png"):
    """Vẽ bản đồ lộ trình di chuyển của các xe và lưu thành file ảnh."""
    plt.figure(figsize=(10, 8))
    
    # 1. Vẽ các điểm khách hàng (Màu xanh)
    cx = [c['x'] for c in data_loader.customers]
    cy = [c['y'] for c in data_loader.customers]
    plt.scatter(cx, cy, c='blue', s=20, label='Khách hàng')
    
    # 2. Vẽ Kho trung tâm - Depot (Hình vuông đỏ)
    plt.scatter(data_loader.depot['x'], data_loader.depot['y'], c='red', marker='s', s=100, label='Depot')
    
    # 3. Tạo màu ngẫu nhiên cho mỗi xe
    colors = plt.cm.tab20(np.linspace(0, 1, len(best_solution.routes)))
    
    # 4. Vẽ đường đi cho từng tuyến
    for i, route in enumerate(best_solution.routes):
        route_x = [data_loader.depot['x']]
        route_y = [data_loader.depot['y']]
        
        for cust_idx in route:
            cust = data_loader.customers[cust_idx - 1]
            route_x.append(cust['x'])
            route_y.append(cust['y'])
            
        # Quay về kho
        route_x.append(data_loader.depot['x'])
        route_y.append(data_loader.depot['y'])
        
        plt.plot(route_x, route_y, color=colors[i], alpha=0.6, linewidth=2)
        
    plt.title(f"Bản đồ Lộ trình VRPTW\nSố xe (K): {len(best_solution.routes)} | Tổng khoảng cách (D): {best_solution.total_distance:.2f}")
    plt.legend()
    plt.grid(True)
    
    # 5. Lưu vào thư mục results
    os.makedirs('results', exist_ok=True)
    save_path = os.path.join('results', filename)
    plt.savefig(save_path)
    print(f"📸 Đã vẽ xong và lưu bản đồ tại: {save_path}")
    plt.close()