package com.example.bad;

import java.sql.DriverManager;
import java.sql.Connection;
import java.util.*;
import java.util.regex.Pattern;

/**
 * EJEMPLO DE CÓDIGO CON ANTI-PATRONES
 * Este archivo contiene intencionalmente problemas de performance
 * para demostrar el analizador
 */
public class BadCodeExample {
    
    // ❌ CRITICAL: Static collection sin límite (Memory Leak)
    private static final Map<String, Object> CACHE = new HashMap<>();
    
    // ❌ HIGH: ThreadLocal sin cleanup visible
    private static ThreadLocal<UserContext> userContext = new ThreadLocal<>();
    
    // ❌ LOW: Eager initialization
    private final HeavyObject heavyObj = new HeavyObject();
    
    public void processOrders(List<Long> orderIds) {
        // ❌ CRITICAL: N+1 Query Problem
        for (Long orderId : orderIds) {
            Order order = orderRepository.findById(orderId);
            processOrder(order);
        }
    }
    
    public void processUsers(List<User> users) {
        // ❌ HIGH: Save en loop (no batch)
        for (User user : users) {
            userRepository.save(user);
        }
    }
    
    public String generateReport(List<Item> items) {
        // ❌ HIGH: String concatenation en loop
        String report = "";
        for (Item item : items) {
            report += "Item: " + item.getName() + "\n";
            report += "Price: " + item.getPrice() + "\n";
        }
        return report;
    }
    
    public void validateEmails(List<String> emails) {
        // ❌ HIGH: Pattern compilation en loop
        for (String email : emails) {
            if (email.matches("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}")) {
                processEmail(email);
            }
        }
    }
    
    public List<Result> matchCustomersWithOrders(
            List<Customer> customers, 
            List<Order> orders) {
        
        // ❌ CRITICAL: Nested loops O(N²)
        List<Result> results = new ArrayList<>();
        for (Customer customer : customers) {
            for (Order order : orders) {
                if (order.getCustomerId().equals(customer.getId())) {
                    results.add(new Result(customer, order));
                }
            }
        }
        return results;
    }
    
    public Connection getConnection() throws Exception {
        // ❌ CRITICAL: Sin connection pool
        return DriverManager.getConnection("jdbc:mysql://localhost/db", "user", "pass");
    }
    
    public void processAsync() {
        // ❌ HIGH: Thread creation directa
        new Thread(() -> {
            doHeavyWork();
        }).start();
    }
    
    // ❌ MEDIUM: Synchronized method (lock muy amplio)
    public synchronized void updateCache(String key, Object value) {
        CACHE.put(key, value);
    }
    
    // ❌ MEDIUM: SynchronizedMap en lugar de ConcurrentHashMap
    private Map<String, String> sessionData = 
        Collections.synchronizedMap(new HashMap<>());
    
    // ❌ MEDIUM: Autoboxing en collections
    public List<Integer> getNumbers() {
        List<Integer> numbers = new ArrayList<>();
        for (int i = 0; i < 1000000; i++) {
            numbers.add(i); // Autoboxing: int → Integer
        }
        return numbers;
    }
    
    // ❌ MEDIUM: Stream en loop (hot path)
    public void processData(List<List<Integer>> dataList) {
        for (List<Integer> data : dataList) {
            List<Integer> filtered = data.stream()
                .filter(x -> x > 10)
                .map(x -> x * 2)
                .collect(Collectors.toList());
            process(filtered);
        }
    }
    
    // ❌ MEDIUM: findAll() sin paginación
    public List<User> getAllUsers() {
        return userRepository.findAll(); // Puede ser millones
    }
    
    // Métodos helper (no implementados, solo para compilación)
    private void processOrder(Order order) {}
    private void processEmail(String email) {}
    private void doHeavyWork() {}
    private void process(List<Integer> data) {}
    
    private interface OrderRepository {
        Order findById(Long id);
    }
    
    private interface UserRepository {
        void save(User user);
        List<User> findAll();
    }
    
    private static class Order {
        Long getCustomerId() { return null; }
    }
    
    private static class Customer {
        Long getId() { return null; }
    }
    
    private static class User {}
    
    private static class Item {
        String getName() { return ""; }
        double getPrice() { return 0.0; }
    }
    
    private static class Result {
        Result(Customer c, Order o) {}
    }
    
    private static class UserContext {}
    
    private static class HeavyObject {}
    
    private OrderRepository orderRepository;
    private UserRepository userRepository;
}