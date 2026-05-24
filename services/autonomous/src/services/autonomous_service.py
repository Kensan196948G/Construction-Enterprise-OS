"""自律型AIエージェント・デジタルツイン管理サービス"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import AutonomousAgent, AutonomousTask, ConstructionSimulation, DigitalTwin


# ============================================
# Autonomous Agent CRUD
# ============================================
async def create_agent(db: AsyncSession, data: dict) -> AutonomousAgent:
    agent = AutonomousAgent(
        organization_id=data["organization_id"],
        name=data["name"],
        agent_type=data["agent_type"],
        target_resource=data.get("target_resource"),
        config=data.get("config", {}),
        is_enabled=data.get("is_enabled", True),
        status="idle",
    )
    db.add(agent)
    await db.flush()
    return agent


async def get_agent_by_id(db: AsyncSession, agent_id: UUID) -> AutonomousAgent | None:
    result = await db.execute(
        select(AutonomousAgent).where(AutonomousAgent.id == agent_id)
    )
    return result.scalar_one_or_none()


async def get_agents_paginated(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    agent_type: str | None = None,
    status: str | None = None,
    organization_id: UUID | None = None,
) -> tuple[list[AutonomousAgent], int]:
    query = select(AutonomousAgent)
    count_query = select(func.count(AutonomousAgent.id))

    if agent_type:
        query = query.where(AutonomousAgent.agent_type == agent_type)
        count_query = count_query.where(AutonomousAgent.agent_type == agent_type)
    if status:
        query = query.where(AutonomousAgent.status == status)
        count_query = count_query.where(AutonomousAgent.status == status)
    if organization_id:
        query = query.where(AutonomousAgent.organization_id == organization_id)
        count_query = count_query.where(AutonomousAgent.organization_id == organization_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(AutonomousAgent.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    agents = list(result.scalars().all())

    return agents, total


async def update_agent(db: AsyncSession, agent_id: UUID, data: dict) -> AutonomousAgent | None:
    result = await db.execute(select(AutonomousAgent).where(AutonomousAgent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        return None

    for key, value in data.items():
        if hasattr(agent, key) and value is not None:
            setattr(agent, key, value)

    await db.flush()
    return agent


async def delete_agent(db: AsyncSession, agent_id: UUID) -> bool:
    result = await db.execute(select(AutonomousAgent).where(AutonomousAgent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        return False
    await db.delete(agent)
    await db.flush()
    return True


async def start_agent(db: AsyncSession, agent_id: UUID) -> AutonomousAgent | None:
    result = await db.execute(select(AutonomousAgent).where(AutonomousAgent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        return None
    agent.status = "active"
    agent.last_run_at = datetime.now(timezone.utc)
    agent.run_count += 1
    await db.flush()
    return agent


async def stop_agent(db: AsyncSession, agent_id: UUID) -> AutonomousAgent | None:
    result = await db.execute(select(AutonomousAgent).where(AutonomousAgent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        return None
    agent.status = "idle"
    await db.flush()
    return agent


async def pause_agent(db: AsyncSession, agent_id: UUID) -> AutonomousAgent | None:
    result = await db.execute(select(AutonomousAgent).where(AutonomousAgent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        return None
    agent.status = "paused"
    await db.flush()
    return agent


# ============================================
# Digital Twin CRUD
# ============================================
async def create_twin(db: AsyncSession, data: dict) -> DigitalTwin:
    twin = DigitalTwin(
        organization_id=data["organization_id"],
        project_id=data.get("project_id"),
        name=data["name"],
        twin_type=data["twin_type"],
        bim_model_id=data.get("bim_model_id"),
        iot_device_ids=data.get("iot_device_ids", []),
        sync_interval_seconds=data.get("sync_interval_seconds", 60),
        data_sources=data.get("data_sources", {}),
        metadata_=data.get("metadata", {}),
        status="initializing",
    )
    db.add(twin)
    await db.flush()
    return twin


async def get_twin_by_id(db: AsyncSession, twin_id: UUID) -> DigitalTwin | None:
    result = await db.execute(
        select(DigitalTwin).where(DigitalTwin.id == twin_id)
    )
    return result.scalar_one_or_none()


async def get_twins_paginated(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    twin_type: str | None = None,
    status: str | None = None,
    project_id: UUID | None = None,
    organization_id: UUID | None = None,
) -> tuple[list[DigitalTwin], int]:
    query = select(DigitalTwin)
    count_query = select(func.count(DigitalTwin.id))

    if twin_type:
        query = query.where(DigitalTwin.twin_type == twin_type)
        count_query = count_query.where(DigitalTwin.twin_type == twin_type)
    if status:
        query = query.where(DigitalTwin.status == status)
        count_query = count_query.where(DigitalTwin.status == status)
    if project_id:
        query = query.where(DigitalTwin.project_id == project_id)
        count_query = count_query.where(DigitalTwin.project_id == project_id)
    if organization_id:
        query = query.where(DigitalTwin.organization_id == organization_id)
        count_query = count_query.where(DigitalTwin.organization_id == organization_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(DigitalTwin.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    twins = list(result.scalars().all())

    return twins, total


async def update_twin(db: AsyncSession, twin_id: UUID, data: dict) -> DigitalTwin | None:
    result = await db.execute(select(DigitalTwin).where(DigitalTwin.id == twin_id))
    twin = result.scalar_one_or_none()
    if not twin:
        return None

    for key, value in data.items():
        if hasattr(twin, key) and value is not None:
            if key == "metadata":
                setattr(twin, "metadata_", value)
            else:
                setattr(twin, key, value)

    await db.flush()
    return twin


async def delete_twin(db: AsyncSession, twin_id: UUID) -> bool:
    result = await db.execute(select(DigitalTwin).where(DigitalTwin.id == twin_id))
    twin = result.scalar_one_or_none()
    if not twin:
        return False
    await db.delete(twin)
    await db.flush()
    return True


async def sync_twin(
    db: AsyncSession, twin_id: UUID, current_state: dict
) -> DigitalTwin | None:
    result = await db.execute(select(DigitalTwin).where(DigitalTwin.id == twin_id))
    twin = result.scalar_one_or_none()
    if not twin:
        return None

    now = datetime.now(timezone.utc)
    twin.last_sync_at = now
    twin.current_state = current_state
    twin.status = "active"
    await db.flush()
    return twin


async def get_twin_current_state(db: AsyncSession, twin_id: UUID) -> dict | None:
    result = await db.execute(select(DigitalTwin).where(DigitalTwin.id == twin_id))
    twin = result.scalar_one_or_none()
    if not twin:
        return None
    return {
        "twin_id": twin.id,
        "name": twin.name,
        "status": twin.status,
        "current_state": twin.current_state,
        "last_sync_at": twin.last_sync_at,
    }


# ============================================
# Autonomous Task CRUD
# ============================================
async def create_task(db: AsyncSession, data: dict) -> AutonomousTask:
    task = AutonomousTask(
        organization_id=data["organization_id"],
        agent_id=data.get("agent_id"),
        digital_twin_id=data.get("digital_twin_id"),
        title=data["title"],
        task_type=data["task_type"],
        priority=data.get("priority", "normal"),
        input_data=data.get("input_data"),
        status="pending",
    )
    db.add(task)
    await db.flush()
    return task


async def get_task_by_id(db: AsyncSession, task_id: UUID) -> AutonomousTask | None:
    result = await db.execute(
        select(AutonomousTask).where(AutonomousTask.id == task_id)
    )
    return result.scalar_one_or_none()


async def get_tasks_paginated(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    task_type: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    agent_id: UUID | None = None,
    organization_id: UUID | None = None,
) -> tuple[list[AutonomousTask], int]:
    query = select(AutonomousTask)
    count_query = select(func.count(AutonomousTask.id))

    if task_type:
        query = query.where(AutonomousTask.task_type == task_type)
        count_query = count_query.where(AutonomousTask.task_type == task_type)
    if status:
        query = query.where(AutonomousTask.status == status)
        count_query = count_query.where(AutonomousTask.status == status)
    if priority:
        query = query.where(AutonomousTask.priority == priority)
        count_query = count_query.where(AutonomousTask.priority == priority)
    if agent_id:
        query = query.where(AutonomousTask.agent_id == agent_id)
        count_query = count_query.where(AutonomousTask.agent_id == agent_id)
    if organization_id:
        query = query.where(AutonomousTask.organization_id == organization_id)
        count_query = count_query.where(AutonomousTask.organization_id == organization_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(AutonomousTask.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    tasks = list(result.scalars().all())

    return tasks, total


# ============================================
# Construction Simulation CRUD
# ============================================
async def create_simulation(db: AsyncSession, data: dict) -> ConstructionSimulation:
    sim = ConstructionSimulation(
        organization_id=data["organization_id"],
        project_id=data.get("project_id"),
        digital_twin_id=data.get("digital_twin_id"),
        name=data["name"],
        simulation_type=data["simulation_type"],
        parameters=data.get("parameters", {}),
        created_by=data.get("created_by"),
        status="draft",
    )
    db.add(sim)
    await db.flush()
    return sim


async def get_simulation_by_id(db: AsyncSession, sim_id: UUID) -> ConstructionSimulation | None:
    result = await db.execute(
        select(ConstructionSimulation).where(ConstructionSimulation.id == sim_id)
    )
    return result.scalar_one_or_none()


async def get_simulations_paginated(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    simulation_type: str | None = None,
    status: str | None = None,
    project_id: UUID | None = None,
    organization_id: UUID | None = None,
) -> tuple[list[ConstructionSimulation], int]:
    query = select(ConstructionSimulation)
    count_query = select(func.count(ConstructionSimulation.id))

    if simulation_type:
        query = query.where(ConstructionSimulation.simulation_type == simulation_type)
        count_query = count_query.where(ConstructionSimulation.simulation_type == simulation_type)
    if status:
        query = query.where(ConstructionSimulation.status == status)
        count_query = count_query.where(ConstructionSimulation.status == status)
    if project_id:
        query = query.where(ConstructionSimulation.project_id == project_id)
        count_query = count_query.where(ConstructionSimulation.project_id == project_id)
    if organization_id:
        query = query.where(ConstructionSimulation.organization_id == organization_id)
        count_query = count_query.where(ConstructionSimulation.organization_id == organization_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(ConstructionSimulation.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    simulations = list(result.scalars().all())

    return simulations, total


async def update_simulation(
    db: AsyncSession, sim_id: UUID, data: dict
) -> ConstructionSimulation | None:
    result = await db.execute(
        select(ConstructionSimulation).where(ConstructionSimulation.id == sim_id)
    )
    sim = result.scalar_one_or_none()
    if not sim:
        return None

    for key, value in data.items():
        if hasattr(sim, key) and value is not None:
            setattr(sim, key, value)

    await db.flush()
    return sim


async def delete_simulation(db: AsyncSession, sim_id: UUID) -> bool:
    result = await db.execute(
        select(ConstructionSimulation).where(ConstructionSimulation.id == sim_id)
    )
    sim = result.scalar_one_or_none()
    if not sim:
        return False
    await db.delete(sim)
    await db.flush()
    return True


async def run_simulation(db: AsyncSession, sim_id: UUID) -> ConstructionSimulation | None:
    result = await db.execute(
        select(ConstructionSimulation).where(ConstructionSimulation.id == sim_id)
    )
    sim = result.scalar_one_or_none()
    if not sim:
        return None

    now = datetime.now(timezone.utc)
    sim.status = "running"
    sim.started_at = now
    sim.progress_percent = 0

    # シミュレーション完了を模擬
    sim.status = "completed"
    sim.completed_at = datetime.now(timezone.utc)
    sim.progress_percent = 100.00
    sim.results = {
        "summary": "Simulation completed successfully",
        "executed_at": now.isoformat(),
    }

    await db.flush()
    return sim
