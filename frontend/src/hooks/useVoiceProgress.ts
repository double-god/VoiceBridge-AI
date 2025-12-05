import { useState, useEffect, useCallback, useRef } from 'react';
import type {
  VoiceProcessStatus,
  ProgressEvent,
  VoiceRecord,
  UseVoiceProgressReturn,
} from '@/types';

//配置常量
//api基础路径，从环境变量读取
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1';

//状态对应的进度百分比映射
//根据在状态估算进度（与后端 calculateProgress 保持一致）
const STATUS_PROGRESS_MAP: Record<VoiceProcessStatus, number> = {
  uploaded: 10,
  processing_asr: 30,
  processing_llm: 60,
  processing_tts: 80,
  completed: 100,
  failed: 0,
  error: 0,
};

//状态对应的中文描述
const STATUS_MESSAGE_MAP: Record<VoiceProcessStatus, string> = {
  uploaded: '已上传，等待处理',
  processing_asr: '语音识别中...',
  processing_llm: 'LLM分析中...',
  processing_tts: '语音合成中...',
  completed: '处理完成',
  failed: '处理失败',
  error: '连接错误',
};

///hook实现
//封装了SSE连接和状态管理的逻辑，只要传入recordId就能使用
export function useVoiceProgress(recordId: number | null): UseVoiceProgressReturn {
  //状态定义
  /**
   * const [state, setState] = useState(initialValue)
   * - state: 当前状态值
   * - setState: 更新状态的函数
   * - initialValue: 初始值
   */
  const [status, setStatus] = useState<VoiceProcessStatus>('uploaded');
  const [progress, setProgress] = useState<number>(0);
  const [message, setMessage] = useState<string>('等待处理...');
  const [result, setResult] = useState<VoiceRecord | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);

  //用useref存储eventsource实例，需要在cleanup时关闭连接，但不要让ui更新
  const eventSourceRef = useRef<EventSource | null>(null);

  //计算属性
  //是否完成，每次status变化时计算
  const isCompleted = status === 'completed' || status === 'failed' || status === 'error';

  //关闭连接的函数
  /**
   * const memoizedFn = useCallback(fn, [deps])
   * - fn: 需要缓存的函数
   * - deps: 依赖数组，只有依赖变化时才会重新创建函数
   * useCallback用于缓存函数，避免每次渲染都创建新函数,这个函数作为prop传递给子组件时可以避免重新渲染，作为useEffect依赖时可以避免重复执行
   */
  const closeConnection = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    }
  }, []); //空依赖数组表示永远不会变化

  //建立SSE连接
  /*
    useEffect(() => { effect }, [deps])
   * - effect: 副作用函数（如网络请求、订阅等）
   * - deps: 依赖数组，依赖变化时重新执行 effect
   * - return: 清理函数，组件卸载或依赖变化前执行
   * 
   * 组件首次挂载后会执行
   * 依赖数组的值变化时会重新执行
   * 组件卸载时会执行清理函数
    */
  useEffect(() => {
    //如果recordId为空，直接返回
    if (!recordId) {
      return;
    }
    //如果已经完成就不重新连接
    if (isCompleted) {
      return;
    }

    //关闭之前的连接（通过直接操作 ref，避免触发 setState）
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    //获取token
    const token = localStorage.getItem('token');
    //构造SSE url,eventsource只能用get请求
    // 后端路径: /voice/status/stream/:id
    const url = `${API_BASE_URL}/voice/status/stream/${recordId}?token=${token || ''}`;

    console.log('[SSE] 正在连接:', url);

    //创建EventSource实例
    //onopen在连接成功时触发,onmessage在收到消息时触发,onerror在连接出错时触发
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    //连接建立成功
    eventSource.onopen = () => {
      console.log('[SSE] 连接已打开');
      setIsConnected(true);
      setError(null);
    };
    //收到服务器推送的消息
    eventSource.onmessage = (event: MessageEvent) => {
      /**
       * 信息结构
       * -event.data:服务器发送的字符串格式数据
       * -event.type:事件类型
       * -event.lastEventId:最后一个事件ID
       */

      try {
        //解析Json数据
        const data: ProgressEvent = JSON.parse(event.data);
        console.log('[SSE] 收到消息:', data);

        //更新状态
        setStatus(data.status);
        //后端给啥就用，没给就根据状态估计或者用默认消息
        setProgress(data.progress ?? STATUS_PROGRESS_MAP[data.status]);
        setMessage(data.message ?? STATUS_MESSAGE_MAP[data.status]);

        //处理完成（后端返回 'completed'）
        if (data.status === 'completed') {
          // 后端完成时返回的是单独字段，不是完整的 VoiceRecord
          // 构造一个部分结果对象
          if (data.asr_text || data.refined_text || data.tts_url) {
            setResult({
              id: recordId!,
              user_id: 0,
              minio_bucket: '',
              minio_key: '',
              duration: 0,
              status: 'completed',
              analysis_result: {
                id: 0,
                voice_record_id: recordId!,
                asr_text: data.asr_text || '',
                refined_text: data.refined_text || '',
                confidence: 0,
                decision: (data.decision as 'accept' | 'reject' | 'boundary') || 'accept',
                tts_audio_url: data.tts_url || '',
                created_at: '',
              },
              created_at: '',
              updated_at: '',
            });
          }
          closeConnection();
        }

        //处理失败（后端返回 'failed' 或 'error'）
        if (data.status === 'failed' || data.status === 'error') {
          setError(data.msg || data.error || '未知错误');
          closeConnection();
        }
      } catch (e) {
        console.error('[SSE] 解析消息失败:', e);
      }
    };

    //发生错误
    eventSource.onerror = (event: Event) => {
      console.error('[SSE] 连接错误:', event);

      //SSE错误处理，readyState状态：0-连接中，1-已连接，2-已关闭
      if (eventSourceRef.current?.readyState === EventSource.CLOSED) {
        setIsConnected(false);
        setError('连接已关闭');
      }
    };

    //清理函数会在组件卸载，依赖项变化时导致effect重新执行
    //关闭SSE连接，避免内存泄漏，避免组件卸载后还更新
    return () => {
      closeConnection();
    };
  }, [recordId, isCompleted, closeConnection]); //依赖数组

  //返回值
  return {
    status,
    progress,
    message,
    result,
    error,
    isConnected,
    isCompleted,
  };
}

//默认导出
export default useVoiceProgress;
