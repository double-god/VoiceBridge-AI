import { useState } from 'react';
import { AxiosError } from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import type { ApiResponse } from '@/types';
import { register, login } from '@/api/auth';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Loader2, UserPlus, CheckCircle } from 'lucide-react';
import bgImage from '@/assets/bg.png';

export default function RegisterPage() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [fieldErrors, setFieldErrors] = useState({
    username: '',
    password: '',
    confirmPassword: '',
  });
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // 重置错误
    setFieldErrors({ username: '', password: '', confirmPassword: '' });
    setError('');
    setSuccess('');

    // 手动验证
    let hasError = false;
    const newFieldErrors = { username: '', password: '', confirmPassword: '' };

    if (!formData.username) {
      newFieldErrors.username = '请填写此字段';
      hasError = true;
    }
    if (!formData.password) {
      newFieldErrors.password = '请填写此字段';
      hasError = true;
    }
    if (!formData.confirmPassword) {
      newFieldErrors.confirmPassword = '请填写此字段';
      hasError = true;
    }

    if (hasError) {
      setFieldErrors(newFieldErrors);
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }

    setIsLoading(true);

    try {
      // 1. 注册
      const registerRes = await register({
        username: formData.username,
        password: formData.password,
      });

      if (registerRes.code === 0 || registerRes.code === 200) {
        // 2. 注册成功，自动登录
        setSuccess('注册成功，正在自动登录...');
        
        const loginRes = await login({
          username: formData.username,
          password: formData.password,
        });

        if (loginRes.code === 0 || loginRes.code === 200) {
          setSuccess('登录成功，正在跳转...');
          // 延迟跳转，让用户看到成功提示
          setTimeout(() => {
            navigate('/');
          }, 1000);
        } else {
          // 自动登录失败，跳转到登录页让用户手动登录
          setError('自动登录失败，请手动登录');
          setTimeout(() => {
            navigate('/login');
          }, 1500);
        }
      } else {
        setError(registerRes.msg || '注册失败，请重试');
      }
    } catch (err) {
      const error = err as AxiosError<ApiResponse>;
      // 优先显示后端返回的错误信息
      const msg = error.response?.data?.msg || '网络错误，请稍后重试';
      setError(msg);
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
      {/* 黑色遮罩 */}
      <div className="absolute inset-0 bg-black/10 backdrop-blur-[2px]" />

      <Card className="w-[90vw] md:w-[50vw] lg:w-[35vw] shadow-2xl border-white/40 bg-white/30 backdrop-blur-xl z-10 relative p-[4vh]">
        <CardHeader className="space-y-[1vh] text-center pb-[3vh]">
          <div className="mx-auto w-[8vh] h-[8vh] bg-green-600/90 rounded-2xl flex items-center justify-center mb-[2vh] shadow-lg shadow-green-500/30 backdrop-blur-sm">
            <UserPlus className="text-white h-[4vh] w-[4vh]" />
          </div>
          <CardTitle className="text-[3vh] font-bold tracking-tight text-gray-900">
            创建账号
          </CardTitle>
          <p className="text-[1.6vh] text-gray-600 mt-[1vh]">加入 VoiceBridge，开启智能语音之旅</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-[2.5vh]" noValidate>
            <Input
              label="用户名"
              placeholder="设置您的用户名"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              error={fieldErrors.username}
              className="h-[6vh] text-[1.8vh]"
              labelClassName="text-[1.8vh] mb-[1vh]"
              autoComplete="username"
            />
            <Input
              label="密码"
              type="password"
              placeholder="设置您的密码"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              error={fieldErrors.password}
              className="h-[6vh] text-[1.8vh]"
              labelClassName="text-[1.8vh] mb-[1vh]"
              autoComplete="new-password"
            />
            <Input
              label="确认密码"
              type="password"
              placeholder="请再次输入密码"
              value={formData.confirmPassword}
              onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
              error={fieldErrors.confirmPassword}
              className="h-[6vh] text-[1.8vh]"
              labelClassName="text-[1.8vh] mb-[1vh]"
              autoComplete="new-password"
            />

            {error && (
              <div className="animate-in fade-in slide-in-from-top-2 flex items-center gap-[1vh] rounded-[1vh] bg-red-50 p-[1.5vh] text-[1.6vh] md:text-[1.8vh] font-medium text-red-600">
                <span className="h-[1.6vh] w-[0.4vh] rounded-full bg-red-600" />
                {error}
              </div>
            )}

            {success && (
              <div className="animate-in fade-in slide-in-from-top-2 flex items-center gap-[1vh] rounded-[1vh] bg-green-50 p-[1.5vh] text-[1.6vh] md:text-[1.8vh] font-medium text-green-600">
                <CheckCircle className="h-[2vh] w-[2vh] text-green-600" />
                {success}
              </div>
            )}

            <Button
              type="submit"
              className="mt-[2vh] w-full bg-gradient-to-r from-green-600 to-emerald-600 shadow-md transition-all duration-300 hover:from-green-700 hover:to-emerald-700 hover:shadow-lg h-[6vh] text-[1.8vh]"
              size="lg"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-[2vh] w-[2vh] animate-spin" />
                  注册中...
                </>
              ) : (
                '立即注册'
              )}
            </Button>

            <div className="mt-[2vh] text-center text-[1.6vh] text-gray-500">
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
