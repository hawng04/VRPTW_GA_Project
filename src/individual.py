class Individual:
    def __init__(self, chromosome, data_loader):
        self.chromosome = chromosome 
        self.data = data_loader
        self.routes = []
        
        self.total_distance = 0.0
        self.capacity_violation = 0.0
        self.tw_violation = 0.0
        self.z_cost = 0.0
        self.fitness = 0.0
        
        # CHÌA KHÓA TỐI ƯU NẰM Ở ĐÂY: HỆ SỐ PHẠT VỪA PHẢI
        # Nếu phạt 10000 ngay từ đầu, GA sẽ không dám ghép các chuỗi mới 
        # (chỉ cần lệch 1 giây là bị phạt 10000 điểm).
        self.alpha = 50.0  # Phạt tải trọng (Giảm xuống để nới lỏng)
        self.beta = 100.0  # Phạt thời gian (Giảm xuống để nới lỏng)
        self.epsilon = 0.0001 

    def split_to_routes(self):
        """
        Cơ chế Split: Vẫn giữ cắt tuyến tính (vì Prins Split quá phức tạp), 
        nhưng nới lỏng để kết hợp với PFIH và Ruin & Recreate.
        """
        self.routes = []
        current_route = []
        current_load = 0.0
        current_time = 0.0 
        prev_node_id = 0 
        
        for cust_idx in self.chromosome:
            cust = self.data.customers[cust_idx - 1]
            dist = self.data.distance_matrix[prev_node_id][cust_idx]
            arrival_time = current_time + dist
            start_service = max(arrival_time, cust['ready_time'])
            
            if (current_load + cust['demand'] > self.data.vehicle_capacity) or (start_service > cust['due_date']):
                if len(current_route) > 0:
                    self.routes.append(current_route)
                current_route = [cust_idx]
                current_load = cust['demand']
                
                dist_from_depot = self.data.distance_matrix[0][cust_idx]
                arrival_time_new = dist_from_depot
                current_time = max(arrival_time_new, cust['ready_time']) + cust['service_time']
                prev_node_id = cust_idx
            else:
                current_route.append(cust_idx)
                current_load += cust['demand']
                current_time = start_service + cust['service_time']
                prev_node_id = cust_idx
                
        if current_route:
            self.routes.append(current_route)

    def evaluate_fitness(self):
        self.split_to_routes()
        
        self.total_distance = 0.0
        self.capacity_violation = 0.0
        self.tw_violation = 0.0
        
        for route in self.routes:
            route_load = 0.0
            current_time = 0.0
            prev_node_id = 0 
            
            for cust_idx in route:
                cust = self.data.customers[cust_idx - 1]
                dist = self.data.distance_matrix[prev_node_id][cust_idx]
                self.total_distance += dist
                
                arrival_time = current_time + dist
                start_service = max(arrival_time, cust['ready_time']) 
                
                if start_service > cust['due_date']:
                    self.tw_violation += (start_service - cust['due_date'])
                
                current_time = start_service + cust['service_time']
                route_load += cust['demand']
                prev_node_id = cust_idx
                
            dist_to_depot = self.data.distance_matrix[prev_node_id][0]
            self.total_distance += dist_to_depot
            
            arrival_depot = current_time + dist_to_depot
            if arrival_depot > self.data.depot['due_date']:
                self.tw_violation += (arrival_depot - self.data.depot['due_date'])
                
            if route_load > self.data.vehicle_capacity:
                self.capacity_violation += (route_load - self.data.vehicle_capacity)
                
        # HẠ TRỌNG SỐ XE XUỐNG: 
        # Nếu để 10000, xe ít nhưng đường dài. Hạ xuống 1000 sẽ cân bằng cả Số xe và Quãng đường.
        VEHICLE_WEIGHT = 1000.0  
        
        self.z_cost = (len(self.routes) * VEHICLE_WEIGHT) + self.total_distance \
                      + (self.alpha * self.capacity_violation) + (self.beta * self.tw_violation)
                      
        self.fitness = 1.0 / (self.z_cost + self.epsilon)