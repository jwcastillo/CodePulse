# JVM Performance Patterns - Referencia Rápida

## 🔍 Búsqueda Rápida por Síntoma

### Mi aplicación es lenta

| Síntoma | Patrón | Solución | Mejora |
|---------|--------|----------|---------|
| Queries lentas con collections | [N+1 Query](#n1-query-problem) | JOIN FETCH | 100x |
| Loops lentos con String | [String concat in loop](#string-concatenation-in-loop) | StringBuilder | 1000x |
| get() lento en List | [LinkedList random access](#linkedlist-for-random-access) | ArrayList | 2500x |
| Validación regex lenta | [Pattern in method](#pattern-compilation-in-method) | Pre-compile Pattern | 1000x |
| Lectura de archivos lenta | [Unbuffered I/O](#bufferedreaderwriter-not-used) | BufferedReader | 900x |
| Llamadas lentas a métodos | [Reflection in hot path](#reflection-in-performance-critical-path) | Direct call | 500x |
| Cache lento | [Synchronized reads](#synchronized-method-for-read-only-operations) | ConcurrentHashMap | 100x |

### OutOfMemoryError

| Síntoma | Patrón | Solución |
|---------|--------|----------|
| Heap crece indefinidamente | [Static collection](#static-collection-without-cleanup) | Bounded cache |
| Memory leak en threads | [ThreadLocal leak](#threadlocal-not-removed) | Always remove() |
| OOM al leer archivos | [Load file to memory](#reading-entire-file-into-memory) | Stream processing |
| Too many open files | [Resources not closed](#not-closing-resources) | try-with-resources |
| Cache sin límite | [Unbounded cache](#static-collection-without-cleanup) | Caffeine/Guava |

### Bugs en producción

| Síntoma | Patrón | Solución |
|---------|--------|----------|
| Fechas incorrectas bajo carga | [SimpleDateFormat concurrent](#simpledateformat-in-concurrent-context) | DateTimeFormatter |
| HashMap values desaparecen | [Mutable keys](#hashmap-with-mutable-keys) | Immutable keys |
| Race conditions | [Sync on mutable](#synchronizing-on-mutable-object) | Final lock object |
| SQL injection | SQL concat | PreparedStatement |

---

## 📊 Matriz de Patrones

### String Performance

| Patrón | Severidad | Impacto | Solución |
|--------|-----------|---------|----------|
| Concatenation in loop | 🔴 CRITICAL | 1000x | StringBuilder |
| String.format() in loop | 🟠 HIGH | 20x | Direct concat |
| String.split() in loop | 🟠 HIGH | 100x | indexOf() |

### Collections

| Patrón | Severidad | Impacto | Solución |
|--------|-----------|---------|----------|
| LinkedList random access | 🔴 CRITICAL | 2500x | ArrayList |
| ArrayList without capacity | 🟡 MEDIUM | 33% | Set initial capacity |
| HashMap without capacity | 🟡 MEDIUM | 50% | Set initial capacity |
| Mutable keys | 🔴 CRITICAL | Bug | Immutable keys |
| keySet() instead entrySet() | 🟠 HIGH | 2x | Use entrySet() |
| Oversized ArrayList | 🟡 MEDIUM | Memory | Reasonable size |

### Concurrency

| Patrón | Severidad | Impacto | Solución |
|--------|-----------|---------|----------|
| Synchronized reads | 🟠 HIGH | 100x | ReadWriteLock/Concurrent |
| Sync on mutable | 🔴 CRITICAL | Bug | Final lock object |
| SimpleDateFormat shared | 🔴 CRITICAL | Bug | DateTimeFormatter |

### I/O

| Patrón | Severidad | Impacto | Solución |
|--------|-----------|---------|----------|
| Unbuffered I/O | 🔴 CRITICAL | 900x | BufferedReader/Writer |
| Load entire file | 🟠 HIGH | OOM | Stream processing |
| Resources not closed | 🔴 CRITICAL | Leak | try-with-resources |

### Database

| Patrón | Severidad | Impacto | Solución |
|--------|-----------|---------|----------|
| N+1 queries | 🔴 CRITICAL | 100x | JOIN FETCH |
| EAGER fetching | 🟡 MEDIUM | 10x | LAZY + JOIN FETCH |
| Large transaction | 🟠 HIGH | Locks | Batch processing |
| Pool misconfiguration | 🟠 HIGH | Memory | 8-16 connections |

### Memory Leaks

| Patrón | Severidad | Impacto | Solución |
|--------|-----------|---------|----------|
| Static collection | 🔴 CRITICAL | Leak | Bounded cache |
| ThreadLocal leak | 🔴 CRITICAL | Leak | Always remove() |
| Listener not unregistered | 🟠 HIGH | Leak | Unregister |

### Reflection

| Patrón | Severidad | Impacto | Solución |
|--------|-----------|---------|----------|
| Reflection in hot path | 🔴 CRITICAL | 500x | Direct call/MethodHandle |
| Class.forName() repeated | 🟠 HIGH | 100x | Cache classes |

### Autoboxing

| Patrón | Severidad | Impacto | Solución |
|--------|-----------|---------|----------|
| Autoboxing in loop | 🟠 HIGH | 10x | Primitives |
| Boxed in collections | 🟡 MEDIUM | 4x memory | Primitive arrays/Trove |

### Exceptions

| Patrón | Severidad | Impacto | Solución |
|--------|-----------|---------|----------|
| Exception for control flow | 🔴 CRITICAL | 900x | Validation |
| Empty catch block | 🟠 HIGH | Bug | Log and handle |

### Logging

| Patrón | Severidad | Impacto | Solución |
|--------|-----------|---------|----------|
| String concat in log | 🟡 MEDIUM | CPU | Parameterized logging |
| Stack trace in loop | 🟠 HIGH | I/O | Aggregate errors |

---

## 🎯 Top 10 Más Críticos (ordenados por impacto)

1. **String concatenation in loop** - 1000x más lento
   ```java
   // ❌ Malo
   String s = "";
   for (...) s += x;

   // ✅ Bueno
   StringBuilder sb = new StringBuilder();
   for (...) sb.append(x);
   ```

2. **LinkedList random access** - 2500x más lento
   ```java
   // ❌ Malo
   List<String> list = new LinkedList<>();
   for (int i = 0; i < list.size(); i++) {
       String s = list.get(i);
   }

   // ✅ Bueno
   List<String> list = new ArrayList<>();
   ```

3. **Pattern compilation repeated** - 1000x más lento
   ```java
   // ❌ Malo
   public boolean validate(String s) {
       return s.matches("\\d+");
   }

   // ✅ Bueno
   private static final Pattern PATTERN = Pattern.compile("\\d+");
   public boolean validate(String s) {
       return PATTERN.matcher(s).matches();
   }
   ```

4. **Unbuffered I/O** - 900x más lento
   ```java
   // ❌ Malo
   FileReader reader = new FileReader("file.txt");
   int c; while ((c = reader.read()) != -1) { ... }

   // ✅ Bueno
   BufferedReader reader = new BufferedReader(new FileReader("file.txt"));
   String line; while ((line = reader.readLine()) != null) { ... }
   ```

5. **N+1 Query Problem** - 100x más lento
   ```java
   // ❌ Malo
   List<User> users = userRepo.findAll(); // 1 query
   for (User u : users) {
       u.setOrders(orderRepo.findByUserId(u.getId())); // N queries
   }

   // ✅ Bueno
   @Query("SELECT u FROM User u JOIN FETCH u.orders")
   List<User> findAllWithOrders();
   ```

6. **Reflection in hot path** - 500x más lento
   ```java
   // ❌ Malo
   Method m = obj.getClass().getMethod("getName");
   String name = (String) m.invoke(obj);

   // ✅ Bueno
   String name = obj.getName();
   ```

7. **Exception for control flow** - 900x más lento
   ```java
   // ❌ Malo
   try {
       int n = Integer.parseInt(s);
   } catch (NumberFormatException e) {
       n = 0;
   }

   // ✅ Bueno
   int n = s.matches("\\d+") ? Integer.parseInt(s) : 0;
   ```

8. **Synchronized read operations** - 100x más lento
   ```java
   // ❌ Malo
   public synchronized Data get(String key) {
       return map.get(key);
   }

   // ✅ Bueno
   private Map<String, Data> map = new ConcurrentHashMap<>();
   public Data get(String key) {
       return map.get(key);
   }
   ```

9. **String.split() repeated** - 100x más lento
   ```java
   // ❌ Malo
   for (String line : lines) {
       String[] parts = line.split(",");
   }

   // ✅ Bueno
   private static final Pattern COMMA = Pattern.compile(",");
   for (String line : lines) {
       String[] parts = COMMA.split(line);
   }
   ```

10. **SimpleDateFormat concurrent** - Data corruption
    ```java
    // ❌ Malo
    private static final SimpleDateFormat FMT = new SimpleDateFormat("yyyy-MM-dd");

    // ✅ Bueno
    private static final DateTimeFormatter FMT = DateTimeFormatter.ofPattern("yyyy-MM-dd");
    ```

---

## 🔧 Checklist de Code Review

### Performance

- [ ] No hay String concatenation en loops
- [ ] No hay Pattern.compile() o String.matches() en loops
- [ ] No hay reflection en hot paths
- [ ] Collections tienen capacidad inicial cuando se conoce
- [ ] Se usa ArrayList para random access (no LinkedList)
- [ ] I/O usa BufferedReader/Writer
- [ ] No se cargan archivos completos en memoria
- [ ] Se usa try-with-resources para cerrar recursos

### Database

- [ ] No hay N+1 queries (usar JOIN FETCH)
- [ ] EAGER fetching solo cuando necesario
- [ ] Transacciones son cortas (< 1 segundo)
- [ ] Connection pool bien dimensionado (8-16)
- [ ] PreparedStatements para queries dinámicas

### Memory

- [ ] Static collections tienen límite de tamaño
- [ ] ThreadLocal se limpia en finally
- [ ] Listeners se des-registran
- [ ] No hay autoboxing en loops
- [ ] HashMap usa claves inmutables

### Concurrency

- [ ] SimpleDateFormat no se comparte entre threads
- [ ] No se sincroniza en objetos mutables
- [ ] Read operations usan ReadWriteLock o ConcurrentHashMap
- [ ] No hay synchronized en métodos read-only

### Exceptions & Logging

- [ ] Exceptions no se usan para control flow
- [ ] Catch blocks no están vacíos
- [ ] Logging usa parameterized messages
- [ ] No se logea stack trace en loops

---

## 📐 Reglas de Oro

### Strings
1. **StringBuilder en loops** (no +)
2. **Pre-compile Pattern** (no matches())
3. **indexOf() para delimitadores simples** (no split())

### Collections
1. **ArrayList para random access** (no LinkedList)
2. **Set initial capacity** cuando se conoce
3. **entrySet()** para iterar Maps (no keySet())
4. **Immutable keys** en HashMap

### I/O
1. **Siempre buffer** (BufferedReader/Writer)
2. **Stream processing** para archivos grandes
3. **try-with-resources** siempre

### Database
1. **JOIN FETCH** para evitar N+1
2. **LAZY fetching** por default
3. **Batch processing** para operaciones masivas
4. **Pool size = cores * 2** (no 100)

### Concurrency
1. **ConcurrentHashMap** para caches thread-safe
2. **DateTimeFormatter** (no SimpleDateFormat)
3. **Final lock objects** (no mutable)
4. **ReadWriteLock** para read-heavy

### Memory
1. **Bounded caches** (Caffeine, Guava)
2. **Remove ThreadLocal** en finally
3. **Unregister listeners**
4. **WeakHashMap** para caches débiles

---

## 💡 Optimizaciones por Fase

### Fase 1: Quick Wins (1 día)
- Arreglar N+1 queries → 100x mejora
- Arreglar String concatenation en loops → 1000x mejora
- Cambiar LinkedList a ArrayList donde aplique → 2500x mejora

### Fase 2: Performance (1 semana)
- Pre-compilar Patterns
- Buffered I/O
- Initial capacities en collections
- ConcurrentHashMap para caches

### Fase 3: Memory (1 semana)
- Bounded caches
- ThreadLocal cleanup
- Stream processing para archivos grandes
- Lazy fetching

### Fase 4: Concurrency (2 semanas)
- ReadWriteLock
- DateTimeFormatter
- Async logging
- Connection pool tuning

---

## 📱 Comandos Útiles

```bash
# Análisis completo
make analyze

# Generar reporte HTML
make report-html-sample

# Ver patrones específicos
grep "CRITICAL" analysis.txt

# Exportar métricas
make monitor-export

# Deploy en K8s
make k8s-deploy
```

---

## 🎓 Aprendizaje Progresivo

### Nivel 1 (Junior): Los 5 Esenciales
1. String concatenation in loop → StringBuilder
2. Resources not closed → try-with-resources
3. N+1 queries → JOIN FETCH
4. LinkedList random access → ArrayList
5. Unbuffered I/O → BufferedReader

### Nivel 2 (Mid): 10 Patrones Críticos
+ Pattern compilation → Pre-compile
+ Exception control flow → Validation
+ Empty catch blocks → Proper handling
+ Autoboxing in loops → Primitives
+ SimpleDateFormat shared → DateTimeFormatter

### Nivel 3 (Senior): Todos los Patrones
+ Memory leaks (ThreadLocal, static collections, listeners)
+ Concurrency (synchronized reads, mutable locks)
+ Database (EAGER fetching, transaction scope, pool config)
+ Reflection optimization
+ Advanced I/O (memory-mapped files, async)

---

**Documento creado**: 2025-01-04
**Última actualización**: 2025-01-04
**Versión**: 1.0.0
