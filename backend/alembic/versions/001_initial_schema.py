"""Initial schema for AURA database: memories, relationships, collections, search_sessions, evidence, action_history, agent_checkpoints

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-19 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from app.models import VectorType

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector if postgresql
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # memories table
    op.create_table(
        'memories',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('thumbnail_path', sa.String(), nullable=True),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('mime_type', sa.String(), server_default='image/png'),
        sa.Column('content_hash', sa.String(), nullable=True),
        sa.Column('ocr_text', sa.Text(), server_default=''),
        sa.Column('ocr_raw', sa.Text(), server_default=''),
        sa.Column('visual_summary', sa.Text(), server_default=''),
        sa.Column('visual_details', sa.Text(), server_default='{}'),
        sa.Column('visual_objects', sa.Text(), server_default='[]'),
        sa.Column('visual_entities', sa.Text(), server_default='[]'),
        sa.Column('multimodal_provider', sa.String(), server_default='gemini_vision'),
        sa.Column('multimodal_status', sa.String(), server_default='live_vision'),
        sa.Column('provenance_ledger', sa.Text(), server_default='[]'),
        sa.Column('summary', sa.Text(), server_default=''),
        sa.Column('category', sa.String(), server_default='other'),
        sa.Column('entities', sa.Text(), server_default='[]'),
        sa.Column('topics', sa.Text(), server_default='[]'),
        sa.Column('objects', sa.Text(), server_default='[]'),
        sa.Column('application', sa.String(), server_default=''),
        sa.Column('window_title', sa.String(), server_default=''),
        sa.Column('source_type', sa.String(), server_default='upload'),
        sa.Column('clipboard_context', sa.Text(), server_default=''),
        sa.Column('captured_at', sa.DateTime(), nullable=True),
        sa.Column('document_type', sa.String(), server_default=''),
        sa.Column('important_information', sa.Text(), server_default='[]'),
        sa.Column('importance_score', sa.Float(), server_default='0.5'),
        sa.Column('sensitivity_level', sa.String(), server_default='PUBLIC'),
        sa.Column('sensitivity_findings', sa.Text(), server_default='[]'),
        sa.Column('embedding', VectorType(384), nullable=True),
        sa.Column('processing_status', sa.String(), server_default='pending'),
        sa.Column('processing_error', sa.Text(), nullable=True),
        sa.Column('is_locked', sa.Boolean(), server_default='0'),
        sa.Column('is_deleted', sa.Boolean(), server_default='0'),
        sa.Column('is_redacted', sa.Boolean(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_memories_content_hash', 'memories', ['content_hash'])
    op.create_index('ix_memories_category', 'memories', ['category'])
    op.create_index('ix_memories_application', 'memories', ['application'])
    op.create_index('ix_memories_sensitivity_level', 'memories', ['sensitivity_level'])
    op.create_index('ix_memories_processing_status', 'memories', ['processing_status'])
    op.create_index('ix_memories_is_deleted', 'memories', ['is_deleted'])
    op.create_index('ix_memories_created_at', 'memories', ['created_at'])
    op.create_index('ix_memories_status_deleted', 'memories', ['processing_status', 'is_deleted'])
    op.create_index('ix_memories_cat_deleted', 'memories', ['category', 'is_deleted'])
    op.create_index('ix_memories_created_deleted', 'memories', ['created_at', 'is_deleted'])

    # relationships table
    op.create_table(
        'relationships',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('source_memory_id', sa.String(), sa.ForeignKey('memories.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_memory_id', sa.String(), sa.ForeignKey('memories.id', ondelete='CASCADE'), nullable=False),
        sa.Column('relationship_type', sa.String(), nullable=False),
        sa.Column('confidence', sa.Float(), server_default='0.7'),
        sa.Column('reason', sa.Text(), server_default=''),
        sa.Column('evidence', sa.Text(), server_default=''),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_relationships_source_memory_id', 'relationships', ['source_memory_id'])
    op.create_index('ix_relationships_target_memory_id', 'relationships', ['target_memory_id'])
    op.create_index('ix_relationships_relationship_type', 'relationships', ['relationship_type'])
    op.create_index('ix_rel_src_tgt', 'relationships', ['source_memory_id', 'target_memory_id'])

    # collections table
    op.create_table(
        'collections',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), server_default=''),
        sa.Column('type', sa.String(), server_default='cluster'),
        sa.Column('color', sa.String(), server_default='#6366f1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # collection_memories table
    op.create_table(
        'collection_memories',
        sa.Column('collection_id', sa.String(), sa.ForeignKey('collections.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('memory_id', sa.String(), sa.ForeignKey('memories.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('confidence', sa.Float(), server_default='1.0'),
    )

    # search_sessions table
    op.create_table(
        'search_sessions',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('plan', sa.Text(), server_default='[]'),
        sa.Column('result_ids', sa.Text(), server_default='[]'),
        sa.Column('confidence', sa.Float(), server_default='0.0'),
        sa.Column('mode', sa.String(), server_default='search'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # evidence table
    op.create_table(
        'evidence',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('memory_id', sa.String(), sa.ForeignKey('memories.id', ondelete='CASCADE'), nullable=False),
        sa.Column('evidence_type', sa.String(), nullable=False),
        sa.Column('evidence_text', sa.Text(), server_default=''),
        sa.Column('confidence', sa.Float(), server_default='0.7'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_evidence_memory_id', 'evidence', ['memory_id'])

    # action_history table
    op.create_table(
        'action_history',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('memory_id', sa.String(), sa.ForeignKey('memories.id', ondelete='CASCADE'), nullable=False),
        sa.Column('action_type', sa.String(), nullable=False),
        sa.Column('input_text', sa.Text(), server_default=''),
        sa.Column('output_text', sa.Text(), server_default=''),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_action_history_memory_id', 'action_history', ['memory_id'])

    # agent checkpoints tables
    op.create_table(
        'agent_checkpoints',
        sa.Column('thread_id', sa.String(), primary_key=True),
        sa.Column('checkpoint_ns', sa.String(), primary_key=True, server_default=''),
        sa.Column('checkpoint_id', sa.String(), primary_key=True),
        sa.Column('parent_checkpoint_id', sa.String(), nullable=True),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('checkpoint', sa.Text(), nullable=False),
        sa.Column('metadata_json', sa.Text(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'agent_checkpoint_blobs',
        sa.Column('thread_id', sa.String(), primary_key=True),
        sa.Column('checkpoint_ns', sa.String(), primary_key=True, server_default=''),
        sa.Column('channel', sa.String(), primary_key=True),
        sa.Column('version', sa.String(), primary_key=True),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('blob', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'agent_checkpoint_writes',
        sa.Column('thread_id', sa.String(), primary_key=True),
        sa.Column('checkpoint_ns', sa.String(), primary_key=True, server_default=''),
        sa.Column('checkpoint_id', sa.String(), primary_key=True),
        sa.Column('task_id', sa.String(), primary_key=True),
        sa.Column('idx', sa.Integer(), primary_key=True),
        sa.Column('channel', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('blob', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('agent_checkpoint_writes')
    op.drop_table('agent_checkpoint_blobs')
    op.drop_table('agent_checkpoints')
    op.drop_table('action_history')
    op.drop_table('evidence')
    op.drop_table('search_sessions')
    op.drop_table('collection_memories')
    op.drop_table('collections')
    op.drop_table('relationships')
    op.drop_table('memories')
