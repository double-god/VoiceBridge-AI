import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { login } from '@/api/auth';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Loader2, ArrowRight } from 'lucide-react';

export default function LoginPage() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const res = await login(formData);
      if (res.code === 200) {
        navigate('/');
      } else {
        setError(res.msg || '登录失败，请检查用户名和密码');
      }
    } catch (err) {
      setError('网络错误，请稍后重试');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-gray-50 p-4">
      {/* 背景装饰 */}
      <div className="pointer-events-none absolute left-0 top-0 z-0 h-full w-full overflow-hidden">
        <div className="absolute -left-[10%] -top-[30%] h-[70%] w-[70%] rounded-full bg-blue-200/30 blur-3xl" />
        <div className="absolute -right-[10%] top-[20%] h-[60%] w-[60%] rounded-full bg-indigo-200/30 blur-3xl" />
      </div>

      <Card className="z-10 w-full max-w-md border-gray-100 bg-white/80 shadow-xl backdrop-blur-sm">
        <CardHeader className="space-y-1 pb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-blue-600 shadow-lg shadow-blue-200">
            <span className="text-xl font-bold text-white">VB</span>
          </div>
          <CardTitle className="text-2xl font-bold tracking-tight text-gray-900">
            欢迎回来
          </CardTitle>
          <p className="text-sm text-gray-500">登录您的 VoiceBridge 账号以继续</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="用户名"
              placeholder="请输入您的用户名"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              required
            />
            <Input
              label="密码"
              type="password"
              placeholder="请输入您的密码"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
            />

            {error && (
              <div className="animate-in fade-in slide-in-from-top-2 flex items-center gap-2 rounded-md bg-red-50 p-3 text-sm text-red-600">
                <span className="h-4 w-1 rounded-full bg-red-600" />
                {error}
              </div>
            )}

            <Button
              type="submit"
              className="mt-6 w-full bg-gradient-to-r from-blue-600 to-indigo-600 shadow-md transition-all duration-300 hover:from-blue-700 hover:to-indigo-700 hover:shadow-lg"
              size="lg"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  登录中...
                </>
              ) : (
                <>
                  立即登录 <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>

            <div className="mt-4 text-center text-sm text-gray-500">
              还没有账号？{' '}
              <Link
                to="/register"
                className="font-medium text-blue-600 underline-offset-4 hover:text-blue-500 hover:underline"
              >
                立即注册
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
