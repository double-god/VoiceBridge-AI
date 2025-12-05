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
      if (res.code === 0 || res.code === 200) {
        // 如果后端返回了用户信息，则设置；否则初始化一个空对象供用户填写
        setUser(res.data || {
          id: 0,
          username: '',
          role: 'patient',
          name: '',
          age: 0,
          condition: '',
          habits: '',
          common_needs: '',
          created_at: '',
          updated_at: ''
        });
      } else {
        // 如果请求失败，也初始化一个空对象
        setUser({
          id: 0,
          username: '',
          role: 'patient',
          name: '',
          age: 0,
          condition: '',
          habits: '',
          common_needs: '',
          created_at: '',
          updated_at: ''
        });
      }
    } catch (error) {
      console.error('获取用户信息失败', error);
      // 即使错误，也初始化一个空对象让用户可以填写
      setUser({
        id: 0,
        username: '',
        role: 'patient',
        name: '',
        age: 0,
        condition: '',
        habits: '',
        common_needs: '',
        created_at: '',
        updated_at: ''
      });
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
      if (res.code === 0 || res.code === 200) {
        setMessage({ type: 'success', content: '个人信息更新成功！' });
        if (res.data) {
          setUser(res.data);
        }
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

  if (!user) {
    return (
      <div className="flex h-[50vh] flex-col items-center justify-center gap-4">
        <p className="text-gray-500">无法加载用户信息，请重试</p>
        <Button onClick={fetchUser}>重新加载</Button>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-[90vw] space-y-[3vh] py-[4vh] lg:max-w-[80vw] xl:max-w-[75vw]">
      <div className="space-y-[1.5vh]">
        <h1 className="text-[3vh] font-bold tracking-tight text-gray-900 md:text-[4vh] lg:text-[5vh] xl:text-[6vh]">个人信息设置</h1>
        <p className="text-[1.8vh] text-gray-500 md:text-[2vh] lg:text-[2.5vh]">完善您的个人信息，让 AI 助手更懂您的需求。</p>
      </div>

      <form onSubmit={handleSubmit}>
        <Card className="border-gray-200 shadow-lg">
          <CardHeader className="border-b border-gray-100 bg-gray-50/50 py-[3vh]">
            <div className="flex items-center gap-[1.5vh]">
              <UserIcon className="h-[2.5vh] w-[2.5vh] text-blue-600 lg:h-[3.5vh] lg:w-[3.5vh]" />
              <CardTitle className="text-[2.5vh] lg:text-[3.5vh]">基本信息</CardTitle>
            </div>
            <CardDescription className="text-[1.8vh] lg:text-[2.2vh]">这些信息将用于生成个性化的语音服务。</CardDescription>
          </CardHeader>
          <CardContent className="space-y-[3vh] py-[4vh] lg:space-y-[4vh]">
            <div className="grid gap-[3vh] md:grid-cols-2 lg:gap-[4vh]">
              <Input
                label="姓名"
                value={user?.name || ''}
                onChange={(e) => handleChange('name', e.target.value)}
                placeholder="您的称呼"
                className="h-[6vh] text-[1.8vh] lg:h-[7vh] lg:text-[2.2vh]"
                labelClassName="text-[1.8vh] lg:text-[2.2vh] mb-[1vh]"
              />
              <Input
                label="年龄"
                type="number"
                value={user?.age || ''}
                onChange={(e) => handleChange('age', parseInt(e.target.value) || 0)}
                placeholder="您的年龄"
                className="h-[6vh] text-[1.8vh] lg:h-[7vh] lg:text-[2.2vh]"
                labelClassName="text-[1.8vh] lg:text-[2.2vh] mb-[1vh]"
              />
            </div>

            <div className="space-y-[3vh] lg:space-y-[4vh]">
              <div className="space-y-[1.5vh]">
                <label className="text-[1.8vh] font-medium text-gray-700 lg:text-[2.5vh]">健康状况 / 特殊情况</label>
                <textarea
                  className="block min-h-[12vh] w-full rounded-[1.5vh] border border-gray-300 bg-white px-[2vh] py-[1.5vh] text-[1.8vh] text-gray-900 placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 lg:min-h-[15vh] lg:text-[2.5vh]"
                  placeholder="例如：视力不佳、行动不便、需要大字体等..."
                  value={user?.condition || ''}
                  onChange={(e) => handleChange('condition', e.target.value)}
                />
              </div>

              <div className="space-y-[1.5vh]">
                <label className="text-[1.8vh] font-medium text-gray-700 lg:text-[2.5vh]">生活习惯</label>
                <textarea
                  className="block min-h-[12vh] w-full rounded-[1.5vh] border border-gray-300 bg-white px-[2vh] py-[1.5vh] text-[1.8vh] text-gray-900 placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 lg:min-h-[15vh] lg:text-[2.5vh]"
                  placeholder="例如：早睡早起、喜欢听戏曲、每天散步..."
                  value={user?.habits || ''}
                  onChange={(e) => handleChange('habits', e.target.value)}
                />
              </div>

              <div className="space-y-[1.5vh]">
                <label className="text-[1.8vh] font-medium text-gray-700 lg:text-[2.5vh]">常用需求</label>
                <textarea
                  className="block min-h-[12vh] w-full rounded-[1.5vh] border border-gray-300 bg-white px-[2vh] py-[1.5vh] text-[1.8vh] text-gray-900 placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 lg:min-h-[15vh] lg:text-[2.5vh]"
                  placeholder="例如：查询天气、提醒吃药、拨打子女电话..."
                  value={user?.common_needs || ''}
                  onChange={(e) => handleChange('common_needs', e.target.value)}
                />
              </div>
            </div>

            {message.content && (
              <div
                className={cn(
                  'animate-in fade-in slide-in-from-top-2 flex items-center gap-[1.5vh] rounded-[1.5vh] p-[2.5vh] text-[1.8vh] lg:text-[2.2vh]',
                  message.type === 'success'
                    ? 'bg-green-50 text-green-700'
                    : 'bg-red-50 text-red-700'
                )}
              >
                <span
                  className={cn(
                    'h-[1vh] w-[1vh] rounded-full',
                    message.type === 'success' ? 'bg-green-600' : 'bg-red-600'
                  )}
                />
                {message.content}
              </div>
            )}

            <div className="flex justify-end pt-[2vh]">
              <Button type="submit" disabled={isSaving} className="h-[6vh] w-full px-[4vh] text-[1.8vh] md:w-auto lg:h-[7vh] lg:px-[6vh] lg:text-[2.2vh]">
                {isSaving ? (
                  <>
                    <Loader2 className="mr-[1.5vh] h-[2.5vh] w-[2.5vh] animate-spin" />
                    保存中...
                  </>
                ) : (
                  <>
                    <Save className="mr-[1.5vh] h-[2.5vh] w-[2.5vh]" />
                    保存信息
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
