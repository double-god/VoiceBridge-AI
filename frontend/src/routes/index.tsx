import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import HomePage from '@/pages/Home';

// 定义路由表
const router = createBrowserRouter([
  {
    path: '/',
    element: <HomePage />,
  },
  // 未来可以在这里添加更多路由，比如 /history, /login 等
]);

export function AppRoutes() {
  return <RouterProvider router={router} />;
}
