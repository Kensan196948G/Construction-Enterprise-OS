"""AIモデル一覧 API — stub"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class AiModel(BaseModel):
    id: str
    name: str
    model_name: str
    purpose: str
    description: str
    accuracy: float
    last_trained: str
    next_training: str
    data_points: int
    status: str


_MOCK_MODELS = [
    AiModel(
        id="am1",
        name="安全予測モデル",
        model_name="safety-risk-v2",
        purpose="安全リスク予測",
        description="過去の事故データから危険予兆を検出する",
        accuracy=0.923,
        last_trained="2024-05-01",
        next_training="2024-06-01",
        data_points=45230,
        status="active",
    ),
    AiModel(
        id="am2",
        name="進捗予測モデル",
        model_name="progress-forecast-v1",
        purpose="工程進捗予測",
        description="天候・リソースデータから工程遅延を予測する",
        accuracy=0.874,
        last_trained="2024-04-15",
        next_training="2024-05-15",
        data_points=12800,
        status="active",
    ),
    AiModel(
        id="am3",
        name="品質検査AI",
        model_name="quality-vision-v3",
        purpose="画像品質検査",
        description="現場写真からコンクリートひび割れ等を自動検出する",
        accuracy=0.951,
        last_trained="2024-05-10",
        next_training="2024-06-10",
        data_points=89500,
        status="active",
    ),
    AiModel(
        id="am4",
        name="コスト最適化モデル",
        model_name="cost-optimizer-v1",
        purpose="資材調達最適化",
        description="需要予測と価格動向から最適な調達タイミングを提案する",
        accuracy=0.812,
        last_trained="2024-03-20",
        next_training="2024-06-20",
        data_points=5600,
        status="training",
    ),
]


@router.get("/models")
async def list_models(
    per_page: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
):
    start = (page - 1) * per_page
    items = _MOCK_MODELS[start : start + per_page]
    return {"items": [m.model_dump() for m in items], "total": len(_MOCK_MODELS)}
