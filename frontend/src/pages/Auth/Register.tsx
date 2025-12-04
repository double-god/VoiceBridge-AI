import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { register } from '@/api/auth';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Loader2, UserPlus } from 'lucide-react';

export default function RegisterPage() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const res = await register({
        username: formData.username,
        password: formData.password,
      });

      if (res.code === 200) {
        // 注册成功后跳转到登录页
        navigate('/login');
      } else {
        setError(res.msg || '注册失败，请重试');
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
        <div className="absolute -bottom-[30%] -right-[10%] h-[70%] w-[70%] rounded-full bg-green-200/30 blur-3xl" />
        <div className="absolute -left-[10%] top-[10%] h-[50%] w-[50%] rounded-full bg-blue-200/30 blur-3xl" />
      </div>

      <Card className="z-10 w-full max-w-md border-gray-100 bg-white/80 shadow-xl backdrop-blur-sm">
        <CardHeader className="space-y-1 pb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-green-600 shadow-lg shadow-green-200">
            <UserPlus className="h-6 w-6 text-white" />
          </div>
          <CardTitle className="text-2xl font-bold tracking-tight text-gray-900">
            创建账号
          </CardTitle>
          <p className="text-sm text-gray-500">加入 VoiceBridge，开启智能语音之旅</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="用户名"
              placeholder="设置您的用户名"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              required
            />
            <Input
              label="密码"
              type="password"
              placeholder="设置您的密码"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
            />
            <Input
              label="确认密码"
              type="password"
              placeholder="请再次输入密码"
              value={formData.confirmPassword}
              onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
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
              className="mt-6 w-full bg-gradient-to-r from-green-600 to-emerald-600 shadow-md transition-all duration-300 hover:from-green-700 hover:to-emerald-700 hover:shadow-lg"
              size="lg"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  注册中...
                </>
              ) : (
                '立即注册'
              )}
            </Button>

            <div className="mt-4 text-center text-sm text-gray-500">
              已有账号？{' '}
              <Link
                to="/login"
                className="font-medium text-blue-600 underline-offset-4 hover:text-blue-500 hover:underline"
              >
                直接登录
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
