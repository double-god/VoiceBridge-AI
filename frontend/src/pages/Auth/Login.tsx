import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { login } from '@/api/auth';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Loader2, ArrowRight } from 'lucide-react';
import bgImage from '@/assets/bg.png';

export default function LoginPage() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({
    username: '',
    password: '',
  });
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 重置错误
    setFieldErrors({ username: '', password: '' });
    setError('');

    // 手动验证
    let hasError = false;
    const newFieldErrors = { username: '', password: '' };

    if (!formData.username) {
      newFieldErrors.username = '请填写此字段';
      hasError = true;
    }
    if (!formData.password) {
      newFieldErrors.password = '请填写此字段';
      hasError = true;
    }

    if (hasError) {
      setFieldErrors(newFieldErrors);
      return;
    }

    setIsLoading(true);

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
    <div 
      className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-cover bg-center bg-no-repeat"
      style={{ 
        backgroundImage: `url(${bgImage})` 
      }}
    >
      {/* 黑色遮罩，确保背景不会太亮影响文字阅读 */}
      <div className="absolute inset-0 bg-black/10 backdrop-blur-[2px]" />

      <Card className="w-[90vw] md:w-[50vw] lg:w-[35vw] shadow-2xl border-white/40 bg-white/30 backdrop-blur-xl z-10 relative p-[4vh]">
        <CardHeader className="space-y-[1vh] text-center pb-[3vh]">
          <div className="mx-auto w-[8vh] h-[8vh] bg-blue-600/90 rounded-2xl flex items-center justify-center mb-[2vh] shadow-lg shadow-blue-500/30 backdrop-blur-sm">
            <span className="text-white font-bold text-[3vh]">VB</span>
          </div>
          <CardTitle className="text-[3vh] font-bold tracking-tight text-gray-900">
            欢迎回来
          </CardTitle>
          <p className="text-[1.6vh] text-gray-600 mt-[1vh]">登录您的 VoiceBridge 账号以继续</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-[2.5vh]" noValidate>
            <Input
              label="用户名"
              placeholder="请输入您的用户名"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              error={fieldErrors.username}
              className="h-[6vh] text-[1.8vh]"
              labelClassName="text-[1.8vh] mb-[1vh]"
            />
            <Input
              label="密码"
              type="password"
              placeholder="请输入您的密码"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              error={fieldErrors.password}
              className="h-[6vh] text-[1.8vh]"
              labelClassName="text-[1.8vh] mb-[1vh]"
            />

            {error && (
              <div className="animate-in fade-in slide-in-from-top-2 flex items-center gap-[1vh] rounded-[1vh] bg-red-50 p-[1.5vh] text-[1.6vh] md:text-[1.8vh] font-medium text-red-600">
                <span className="h-[1.6vh] w-[0.4vh] rounded-full bg-red-600" />
                {error}
              </div>
            )}

            <Button
              type="submit"
              className="mt-[2vh] w-full bg-gradient-to-r from-blue-600 to-indigo-600 shadow-md transition-all duration-300 hover:from-blue-700 hover:to-indigo-700 hover:shadow-lg h-[6vh] text-[1.8vh]"
              size="lg"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-[2vh] w-[2vh] animate-spin" />
                  登录中...
                </>
              ) : (
                <>
                  立即登录 <ArrowRight className="ml-2 h-[2vh] w-[2vh]" />
                </>
              )}
            </Button>

            <div className="mt-[2vh] text-center text-[1.6vh] text-gray-500">
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
