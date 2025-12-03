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

// 语音状态类型
export type VoiceStatus =
    | 'uploaded'
    | 'processing_asr'
    | 'processing_llm'
    | 'processing_tts'
    | 'done'
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

};

//辅助类型，用于前端组件props或者state
// 历史记录
export type HistoryItem = VoiceRecord;