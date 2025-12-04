import { useState, useEffect } from 'react';
import { getCurrentUser, updateUser } from '@/api/auth';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Loader2, Save, User as UserIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { User } from '@/types';

export default function ProfilePage() {
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [message, setMessage] = useState({ type: '', content: '' });

  useEffect(() => {
    fetchUser();
  }, []);

  const fetchUser = async () => {
    setIsLoading(true);
    try {
      const res = await getCurrentUser();
      if (res.code === 200) {
        setUser(res.data);
      }
    } catch (error) {
      console.error('获取用户信息失败', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    setIsSaving(true);
    setMessage({ type: '', content: '' });

    try {
      const res = await updateUser(user);
      if (res.code === 200) {
        setMessage({ type: 'success', content: '个人画像更新成功！' });
        setUser(res.data);
      } else {
        setMessage({ type: 'error', content: res.msg || '更新失败' });
      }
    } catch (error) {
      console.error('更新失败', error);
      setMessage({ type: 'error', content: '网络错误，请稍后重试' });
    } finally {
      setIsSaving(false);
    }
  };

  const handleChange = (key: keyof User, value: string | number) => {
    if (!user) return;
    setUser({ ...user, [key]: value });
  };

  if (isLoading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">个人画像设置</h1>
        <p className="text-gray-500">完善您的个人信息，让 AI 助手更懂您的需求。</p>
      </div>

      <form onSubmit={handleSubmit}>
        <Card className="border-gray-200 shadow-sm">
          <CardHeader className="border-b border-gray-100 bg-gray-50/50">
            <div className="flex items-center gap-2">
              <UserIcon className="h-5 w-5 text-blue-600" />
              <CardTitle>基本信息</CardTitle>
            </div>
            <CardDescription>这些信息将用于生成个性化的语音服务。</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6 pt-6">
            <div className="grid gap-6 md:grid-cols-2">
              <Input
                label="姓名"
                value={user?.name || ''}
                onChange={(e) => handleChange('name', e.target.value)}
                placeholder="您的称呼"
              />
              <Input
                label="年龄"
                type="number"
                value={user?.age || ''}
                onChange={(e) => handleChange('age', parseInt(e.target.value) || 0)}
                placeholder="您的年龄"
              />
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">健康状况 / 特殊情况</label>
                <textarea
                  className="flex min-h-[80px] w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  placeholder="例如：视力不佳、行动不便、需要大字体等..."
                  value={user?.condition || ''}
                  onChange={(e) => handleChange('condition', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">生活习惯</label>
                <textarea
                  className="flex min-h-[80px] w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  placeholder="例如：早睡早起、喜欢听戏曲、每天散步..."
                  value={user?.habits || ''}
                  onChange={(e) => handleChange('habits', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">常用需求</label>
                <textarea
                  className="flex min-h-[80px] w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  placeholder="例如：查询天气、提醒吃药、拨打子女电话..."
                  value={user?.common_needs || ''}
                  onChange={(e) => handleChange('common_needs', e.target.value)}
                />
              </div>
            </div>

            {message.content && (
              <div
                className={cn(
                  'animate-in fade-in slide-in-from-top-2 flex items-center gap-2 rounded-md p-4',
                  message.type === 'success'
                    ? 'bg-green-50 text-green-700'
                    : 'bg-red-50 text-red-700'
                )}
              >
                <span
                  className={cn(
                    'h-2 w-2 rounded-full',
                    message.type === 'success' ? 'bg-green-600' : 'bg-red-600'
                  )}
                />
                {message.content}
              </div>
            )}

            <div className="flex justify-end pt-4">
              <Button type="submit" disabled={isSaving} className="w-full md:w-auto">
                {isSaving ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    保存中...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    保存画像
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  );
}
