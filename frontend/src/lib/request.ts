import axios from 'axios';
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import type { ApiResponse } from '@/types';

//创建axios实例
//方便统一管理请求配置
const request: AxiosInstance = axios.create({
    //基础路径
    baseURL: import.meta.env.VITE_API_BASE_URL ||'http://localhost:8080/api',
    //请求超时时间
    timeout:25000,
    //默认请求头
    headers: {
        'Content-Type': 'application/json',
    },
});

//请求拦截器，自动注入token，添加请求头，请求日志记录
request.interceptors.request.use(
    //成功回调，在请求发出前执行
    (config) => {
        //获取localstorage里的token
        const token = localStorage.getItem('token');

        //如果token存在，添加到请求头
        if(token){
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },

    //失败回调
    (error) => {
        //让请求方的catch捕获错误
        return Promise.reject(error);

    }
);

// 响应拦截器
//处理数据格式，处理数据错误，提示错误信息
request.interceptors.response.use(
    //HTTP状态码2开头执行
    (response: AxiosResponse<ApiResponse>) => {
        const res = response.data;

        //根据后端约定的code处理业务逻辑
        if(res.code === 0 || res.code === 200){
            return response;
        }
        //业务错误
        console.error('[请求错误]',res.msg);
        return Promise.reject(new Error(res.msg || '请求错误'));
    },

    //HTTP状态码不是2开头执行
    (error) => {
        const status = error.response?.status;
        const message = error.response?.data?.msg|| error.message;

        //不同状态不同处理
        switch (status) {
            case 401:
                //token无效，跳转登录
                localStorage.removeItem('token');
                window.location.href = '/login';
                break;
            case 403:
                //禁止访问，没有权限
                console.error('[权限错误]', message);
                break;
            case 404:
                console.error('[请求错误]', '请求资源不存在');
                break;
            case 500:
                console.error('[服务器错误]', message);
                break;
            default:
                console.error(`[${status}] ${message}`);
        }
        return Promise.reject(error);
    }
);

// 导出封装好的请求方法，简化调用
/**
 * GET请求
 * @param url 请求地址
 * @param config 请求配置
 * @returns Promise<ApiResponse<T>>
 *
 * 泛型<T>让调用方指定返回数据的类型
 */
export async function get<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await request.get<ApiResponse<T>>(url, config);
    return response.data;
}

/**
 * POST请求
 * @param url 请求地址
 * @param data 请求体数据
 * @param config 请求配置
 */

export async function post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await request.post<ApiResponse<T>>(url, data, config);
    return response.data;
}

//put请求
export async function put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await request.put<ApiResponse<T>>(url, data, config);
    return response.data;
}

//delete请求
export async function del<T>(url: string,config?:AxiosRequestConfig):Promise<ApiResponse<T>> {
    const response = await request.delete<ApiResponse<T>>(url,config);
    return response.data;
}

//导出axios实例，方便特殊请求使用
export default request;