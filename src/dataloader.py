import numpy as np
import math

class SolomonDataLoader:
    """
    Lớp xử lý trích xuất dữ liệu từ các tệp chuẩn Solomon (VRPTW).
    """
    def __init__(self, filepath):
        self.filepath = filepath
        self.vehicle_capacity = 0
        self.customers = [] # Danh sách chứa dict thông tin từng khách hàng
        self.depot = {}     # Thông tin Trạm trung chuyển (Kho)
        self.distance_matrix = []
        
    def load_data(self):
        """Đọc và phân tích file .txt của Solomon"""
        with open(self.filepath, 'r') as file:
            lines = file.readlines()
            
            # Đọc sức chứa của xe (Nằm ở dòng thứ 5, index 4)
            self.vehicle_capacity = int(lines[4].split()[1])
            
            # Đọc dữ liệu Khách hàng & Depot (Bắt đầu từ dòng 10, index 9 trở đi)
            for line in lines[9:]:
                parts = line.split()
                if len(parts) >= 7:
                    node = {
                        'id': int(parts[0]),
                        'x': float(parts[1]),
                        'y': float(parts[2]),
                        'demand': float(parts[3]),
                        'ready_time': float(parts[4]),
                        'due_date': float(parts[5]),
                        'service_time': float(parts[6])
                    }
                    if node['id'] == 0:
                        self.depot = node
                    else:
                        self.customers.append(node)
                        
        self._calculate_distance_matrix()
        # print(f"✅ Đã tải file {self.filepath} | Số khách hàng: {len(self.customers)}") # Tạm tắt để lúc chạy 56 file đỡ rác màn hình

    def _calculate_distance_matrix(self):
        """Tính ma trận khoảng cách Euclid giữa tất cả các điểm (Depot + Khách hàng)"""
        all_nodes = [self.depot] + self.customers
        n = len(all_nodes)
        self.distance_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    # TỐI ƯU HÓA: Dùng math.hypot tính khoảng cách nhanh và chính xác hơn pitago thủ công
                    self.distance_matrix[i][j] = math.hypot(
                        all_nodes[i]['x'] - all_nodes[j]['x'],
                        all_nodes[i]['y'] - all_nodes[j]['y']
                    )