// 通用响应结构
export interface ApiResponse<T = unknown> {
  code: number;
  msg: string;
  data: T;
}

// 用户模型
export interface User {
  id: number;
  username: string;
  role: string;
  // 患者画像字段
  name: string;
  age: number;
  condition: string;
  habits: string;
  common_needs: string;
  created_at: string;
  updated_at: string;
}

// 语音状态类型（与后端保持一致）
export type VoiceStatus =
  | 'uploaded'
  | 'processing_asr'
  | 'processing_llm'
  | 'processing_tts'
  | 'completed'
  | 'failed'
  | 'error';

// 语音记录模型
export interface VoiceRecord {
  id: number;
  user_id: number;
  minio_bucket: string;
  minio_key: string;
  duration: number;
  status: VoiceStatus;
  analysis_result?: AnalysisResult;
  created_at: string;
  updated_at: string;
}

// 分析结果模型
export type DecisionType = 'accept' | 'reject' | 'boundary';

export interface AnalysisResult {
  id: number;
  voice_record_id: number;

  asr_text: string;
  refined_text: string;

  confidence: number;
  decision: DecisionType;

  tts_audio_url: string;

  created_at: string;
}

//辅助类型，用于前端组件props或者state
// 历史记录
export type HistoryItem = VoiceRecord;

//SSE进度相关类型
//typescript的type联合类型在编译后会被移除，不会影响运行时性能，enum会编译成js对象，增加运行时开销
// 与后端 Go 的状态值保持一致
export type VoiceProcessStatus =
  | 'uploaded' // 已上传，等待处理
  | 'processing_asr' // 语音识别中
  | 'processing_llm' // LLM分析中
  | 'processing_tts' // 语音合成中
  | 'completed' // 处理完成
  | 'failed' // 处理失败
  | 'error'; // 连接/请求错误

//SSE进度事件
//这个接口定义后端通过SSE发送的进度事件数据结构
export interface ProgressEvent {
  status: VoiceProcessStatus;
  progress: number; //0-100百分比
  message?: string; //可选的状态消息
  // 完成时后端返回的额外字段
  asr_text?: string;
  refined_text?: string;
  tts_url?: string;
  decision?: string;
  // 错误时
  msg?: string;
  error?: string;
}

//hook返回值类型
//让hook返回值有明确类型约束
export interface UseVoiceProgressReturn {
  status: VoiceProcessStatus;
  progress: number;
  message: string;
  error: string | null;
  result: VoiceRecord | null;
  isConnected: boolean;
  isCompleted: boolean;
}
