/**
 * EJEMPLO: Código Next.js con Anti-patrones
 * Este código funciona pero tiene problemas de performance y UX
 */

'use client';  // ❌ HIGH: "use client" innecesario para componente estático

import { useState, useEffect } from 'react';

// ❌ HIGH: Client component cuando puede ser Server Component
export default function UserList({ initialUsers }) {
  return (
    <ul>
      {initialUsers.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
  // No usa hooks ni eventos = puede ser Server Component
}

// ❌ MEDIUM: Fetch en cliente cuando puede ser servidor
function Dashboard() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetch('/api/dashboard')  // 🔴 Fetch en cliente
      .then(r => r.json())
      .then(setData);
  }, []);
  
  return <div>{data?.title}</div>;
}

// ❌ HIGH: <img> en lugar de next/image
function Hero() {
  return (
    <div>
      <img src="/hero.jpg" alt="Hero" />  {/* 🔴 Sin optimización */}
      {/* Sin lazy load, sin WebP, sin responsive, layout shift */}
    </div>
  );
}

// ❌ MEDIUM: next/image sin sizes prop
import Image from 'next/image';

function Gallery() {
  return (
    <Image
      src="/photo.jpg"
      alt="Photo"
      width={800}
      height={600}
      // 🔴 Sin sizes = carga imagen incorrecta para viewport
    />
  );
}

// ❌ MEDIUM: Google Fonts sin next/font
// pages/_document.js
import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html>
      <Head>
        <link  {/* 🔴 FOUT, layout shift */}
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap"
          rel="stylesheet"
        />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}

// ❌ HIGH: getServerSideProps para datos estáticos
export async function getServerSideProps() {
  const posts = await fetch('https://api.example.com/posts')  // 🔴 Fetch en cada request
    .then(r => r.json());
  
  return { props: { posts } };
  // Debería ser getStaticProps + ISR
}

// ❌ MEDIUM: getStaticProps sin revalidate
export async function getStaticProps() {
  const data = await fetch('https://api.example.com/data')
    .then(r => r.json());
  
  return {
    props: { data }
    // 🔴 Sin revalidate = nunca se actualiza post-build
  };
}

// ❌ MEDIUM: fetch() sin cache config en App Router
async function PostsPage() {
  const posts = await fetch('https://api.example.com/posts');  // 🔴 Sin cache config
  const data = await posts.json();
  
  return <div>{data.map(p => <Post key={p.id} {...p} />)}</div>;
}

// ❌ HIGH: Import completo de librería grande
import _ from 'lodash';  // 🔴 +50KB cuando solo necesitas 1 función

function Utils() {
  const debouncedFn = _.debounce(handleSearch, 300);
  return <input onChange={debouncedFn} />;
}

// ❌ MEDIUM: Componente pesado sin dynamic import
import HeavyChart from './HeavyChart';  // 🔴 Siempre en bundle inicial

function Analytics() {
  return <HeavyChart data={data} />;
  // Debería usar dynamic import
}

// ❌ HIGH: useEffect sin dependencies array
function BadEffect({ userId }) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {  // 🔴 Loop infinito
    fetchUser(userId).then(setUser);
    // Sin dependencies = ejecuta en cada render
  });
  
  return <div>{user?.name}</div>;
}

// ❌ MEDIUM: useEffect con fetch (hacer en server)
function ClientFetch({ userId }) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetch(`/api/users/${userId}`)  // 🔴 Fetch en cliente
      .then(r => r.json())
      .then(setUser);
  }, [userId]);
  
  return <div>{user?.name}</div>;
  // Debería ser Server Component
}

// ❌ LOW: Función inline en prop
function InlineFunction({ items }) {
  return (
    <List
      items={items}
      onItemClick={(item) => {  // 🔴 Nueva función en cada render
        console.log(item);
      }}
    />
  );
  // Causa re-renders innecesarios de List
}

// ❌ MEDIUM: .map() sin key
function NoKeys({ items }) {
  return (
    <ul>
      {items.map(item => (  // 🔴 Sin key prop
        <li>{item.name}</li>
      ))}
    </ul>
  );
}

// ❌ MEDIUM: Page sin metadata export
// app/blog/page.tsx
export default function BlogPage() {
  return <div>Blog</div>;
  // 🔴 Sin export metadata = SEO degradado
}

// ❌ MEDIUM: API route sin validación de método
// pages/api/users.js
export default function handler(req, res) {  // 🔴 Sin req.method check
  const users = getUsers();
  res.json(users);
  // Acepta GET, POST, DELETE, etc sin validar
}

// ❌ LOW: API route sin CORS
// pages/api/public-data.js
export default function handler(req, res) {
  res.json({ data: 'public' });
  // 🔴 Sin CORS headers = errores en producción
}

// ❌ MEDIUM: No usar useMemo para cálculos costosos
function ExpensiveCalculation({ items }) {
  const total = calculateExpensiveTotal(items);  // 🔴 Recalcula cada render
  
  return <div>Total: {total}</div>;
  // Debería usar useMemo
}

// ❌ LOW: No usar useCallback para funciones
function ParentComponent() {
  const [count, setCount] = useState(0);
  
  const handleClick = () => {  // 🔴 Nueva función cada render
    setCount(c => c + 1);
  };
  
  return <ChildComponent onClick={handleClick} />;
  // Causa re-render de ChildComponent
}

// ❌ CRITICAL: Promise sin error handling en Server Component
async function UnsafeServerComponent() {
  const data = await fetch('https://api.example.com/data')
    .then(r => r.json());  // 🔴 Sin .catch()
  
  return <div>{data.title}</div>;
  // Si falla, error page en producción
}

// ❌ HIGH: Usar lodash completo en lugar de individual
import lodash from 'lodash';  // 🔴 Bundle +50KB

function Component() {
  const debounced = lodash.debounce(fn, 300);
  return <input onChange={debounced} />;
}

// ❌ MEDIUM: No lazy load de componentes pesados
import RichTextEditor from 'react-quill';  // 🔴 +100KB en bundle inicial

function Editor() {
  return <RichTextEditor />;
  // Debería usar dynamic import con ssr: false
}

// Helper functions
function handleSearch() {}
function fetchUser(id) { return Promise.resolve({}); }
function getUsers() { return []; }
function calculateExpensiveTotal(items) { return items.length; }
function fn() {}

const data = [];
const List = ({ items, onItemClick }) => null;
const ChildComponent = ({ onClick }) => null;
const Post = (props) => null;