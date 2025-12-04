import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { LogOut, User, Mic } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { logout } from '@/api/auth';

export default function MainLayout() {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="flex min-h-screen flex-col bg-gray-50">
      {/* 顶部导航栏 - 玻璃拟态效果 */}
      <header className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white/80 backdrop-blur-md supports-[backdrop-filter]:bg-white/60">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 font-bold text-white shadow-lg shadow-blue-200">
              VB
            </div>
            <span className="bg-gradient-to-r from-blue-700 to-indigo-700 bg-clip-text text-xl font-bold text-transparent">
              VoiceBridge
            </span>
          </div>

          <nav className="flex items-center gap-1 md:gap-2">
            <Link to="/">
              <Button
                variant={isActive('/') ? 'primary' : 'ghost'}
                size="sm"
                leftIcon={<Mic className="h-4 w-4" />}
              >
                语音助手
              </Button>
            </Link>
            <Link to="/profile">
              <Button
                variant={isActive('/profile') ? 'primary' : 'ghost'}
                size="sm"
                leftIcon={<User className="h-4 w-4" />}
              >
                个人画像
              </Button>
            </Link>
            <div className="mx-2 h-6 w-px bg-gray-200" />
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="text-gray-500 hover:bg-red-50 hover:text-red-600"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </nav>
        </div>
      </header>

      {/* 主要内容区域 */}
      <main className="animate-in fade-in container mx-auto flex-1 px-4 py-8 duration-500">
        <Outlet />
      </main>

      <footer className="border-t border-gray-100 bg-white py-6 text-center text-sm text-gray-400">
        <p>© 2025 VoiceBridge AI. 为您提供最贴心的语音服务。</p>
      </footer>
    </div>
  );
}
