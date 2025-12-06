//语音相关api
import { get, post } from '@/lib/request';
import type { VoiceRecord, ApiResponse } from '@/types';

//类型定义
export interface UploadResponse {
  record_id: number;
  minio_key: string;
}
//历史记录查询参数
export interface HistoryParams {
  page?: number;
  page_size?: number;
}

//历史记录响应
export interface HistoryResponse {
  records: VoiceRecord[];
  total: number;
}

//SSE进度事件数据
export interface ProgressEvent {
  status: string;
  progress: number;
  message?: string;
  result?: VoiceRecord;
}

//API函数封装
//上传音频文件
export async function uploadAudio(file: Blob): Promise<ApiResponse<UploadResponse>> {
  // FormData 浏览器原生 API，构造表单数据
  const formData = new FormData();

  formData.append('file', file, 'recording.webm');

  // 浏览器会自动设置为 multipart/form-data; boundary=----WebKitFormBoundary...
  // 如果手动设置，就没有 boundary，后端无法解析
  return post<UploadResponse>('/voice/upload', formData);
}

//获取历史记录
export async function getHistory(params?: HistoryParams): Promise<ApiResponse<HistoryResponse>> {
  return get<HistoryResponse>('/voice/history', { params });
}

/**SSE获取处理进度
 * @param recordId 语音记录ID
 * @param onProgress 进度回调函数
 * @param onComplete 完成回调函数
 * @param onError 错误回调函数
 * @returns
 */
export function subscribeProgress(
  recordId: number,
  onProgress: (event: ProgressEvent) => void,
  onComplete: (event: VoiceRecord) => void,
  onError: (error: Event) => void
): () => void {
  //获取api基础路径
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
  //获取token
  const token = localStorage.getItem('token');
  //构造sse url,eventsource只能用get请求
  const url = `${baseUrl}/voice/status/stream/${recordId}?token=${token}`;
  //创建eventsource实例,专门用于接受SSE
  const eventSource = new EventSource(url);

  //监听消息事件
  //服务器发送数据，就会执行这个回调
  eventSource.onmessage = (event) => {
    try {
      //服务器发送的数据在event.data里
      const data: ProgressEvent = JSON.parse(event.data);

      //根据状态判断进度更新还是完成
      if (data.status === 'done' && data.result) {
        onComplete(data.result);
      } else {
        onProgress(data);
      }
    } catch (error) {
      console.error('解析进度事件失败', error);
    }
  };

  //监听错误事件
  eventSource.onerror = (error) => {
    onError(error);
    eventSource.close();
  };

  //返回一个函数，用于关闭连接
  return () => {
    eventSource.close();
  };

  //返回关闭函数
  return () => {
    eventSource.close();
  };
}

//取消任务
export async function cancelVoiceTask(recordId: number): Promise<ApiResponse<{ message: string }>> {
  return fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1'}/voice/cancel/${recordId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
  }).then(res => res.json());
}

//导出为命名空间
export const voiceApi = {
  uploadAudio,
  getHistory,
  subscribeProgress,
  cancelVoiceTask,
};
