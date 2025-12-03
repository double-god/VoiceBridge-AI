//封装与用户认证相关的接口
import { post, get } from '@/lib/request';
import type { User, ApiResponse } from '@/types';

//定义请求/响应的类型
//登录请求参数
export interface LoginRequest {
  username: string;
  password: string;
}

//登录响应数据
export interface LoginResponse {
  token: string;
  user: User;
}

//注册请求参数
export interface RegisterRequest {
  username: string;
  password: string;
}

//封装api函数
export async function login(data: LoginRequest): Promise<ApiResponse<LoginResponse>> {
  //post<loginResponse>指定响应数据类型
  const result = await post<LoginResponse>('/user/login', data);

  //登录成功后，保存token到本地存储
  if (result.data?.token) {
    localStorage.setItem('token', result.data.token);
  }

  return result;
}

//用户注册

export async function register(data: RegisterRequest): Promise<ApiResponse<User>> {
  return post<User>('/user/register', data);
}

//获取当前用户信息。请求拦截器会自动添加authorization头
export async function getCurrentUser(): Promise<ApiResponse<User>> {
  return get<User>('/user/me');
}

//用户登出，清除本地token
export function logout(): void {
  localStorage.removeItem('token');
  window.location.href = '/login';
}

//导出为命名空间
export const authApi = {
  login,
  register,
  getCurrentUser,
  logout,
};
