#!/usr/bin/env python3
"""
Red Paperclip Hackathon Dashboard
Clean, minimal visual dashboard showcasing real metrics from agent simulations
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import glob
from typing import Dict, List, Any
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_session_logs() -> List[Dict[str, Any]]:
    """Load all available session logs."""
    log_dir = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), 'simulation_logs')
    log_files = glob.glob(os.path.join(log_dir, 'demo_session_*.json'))

    sessions = []
    for log_file in sorted(log_files, reverse=True):  # Most recent first
        try:
            with open(log_file, 'r') as f:
                data = json.load(f)
                session_info = {
                    'filename': os.path.basename(log_file),
                    'filepath': log_file,
                    'timestamp': os.path.basename(log_file).replace('demo_session_', '').replace('.json', ''),
                    'events': data,
                    'event_count': len(data)
                }
                sessions.append(session_info)
        except Exception as e:
            st.warning(f"Could not load {log_file}: {e}")

    return sessions


def analyze_session_metrics(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze session events to extract key metrics."""
    metrics = {
        'total_events': len(events),
        'trades_completed': 0,
        'coalitions_formed': 0,
        'chaos_events': 0,
        'x402_payments': 0,
        'x402_success_rate': 0.0,
        'nft_mints': 0,
        'persuasion_pitches': 0,
        'agents_active': set(),
        'trade_values': [],
        'event_timeline': [],
        'recent_pitches': [],
        'payment_receipts': [],
        'latest_capsule': None
    }

    successful_payments = 0
    total_payments = 0

    for event in events:
        event_type = event.get('event_type', '')
        details = event.get('details', {})

        # Count different event types
        if event_type == 'trade_proposal' and details.get('accepted', False):
            metrics['trades_completed'] += 1
            if 'value' in details.get('trade_proposal', {}):
                metrics['trade_values'].append(
                    details['trade_proposal']['value'])

        elif event_type == 'coalition_formation':
            metrics['coalitions_formed'] += 1

        elif event_type == 'chaos_event':
            metrics['chaos_events'] += 1

        elif event_type == 'x402_payment':
            metrics['x402_payments'] += 1
            total_payments += 1

            # Create payment receipt
            receipt = {
                'timestamp': event.get('timestamp', ''),
                'correlation_id': event.get('correlation_id', ''),
                'amount': details.get('amount', 0),
                'status': details.get('status', 'unknown'),
                'agent_id': details.get('agent_id', 'unknown')
            }
            metrics['payment_receipts'].append(receipt)

            if details.get('status') == 'success':
                successful_payments += 1

        elif event_type == 'nft_minting':
            metrics['nft_mints'] += 1

        elif event_type == 'persuasion_pitch':
            metrics['persuasion_pitches'] += 1
            pitch_info = {
                'timestamp': event.get('timestamp', ''),
                'from_agent': details.get('from_agent', ''),
                'to_agent': details.get('to_agent', ''),
                'pitch': details.get('pitch_text', '')[:100] + '...' if len(details.get('pitch_text', '')) > 100 else details.get('pitch_text', ''),
                'cost': details.get('cost', 0)
            }
            metrics['recent_pitches'].append(pitch_info)

        elif event_type == 'capsule_snapshot':
            metrics['latest_capsule'] = details

        # Track active agents
        for key in ['agent_id', 'from_agent', 'to_agent']:
            if key in details:
                metrics['agents_active'].add(details[key])

        # Build timeline
        metrics['event_timeline'].append({
            'timestamp': event.get('timestamp', ''),
            'step': event.get('step', 0),
            'event_type': event_type,
            'correlation_id': event.get('correlation_id', '')
        })

    # Calculate payment success rate
    if total_payments > 0:
        metrics['x402_success_rate'] = (
            successful_payments / total_payments) * 100

    metrics['agents_active'] = len(metrics['agents_active'])

    return metrics


def create_trade_timeline_chart(timeline: List[Dict[str, Any]]) -> go.Figure:
    """Create timeline chart showing trades over steps."""
    df = pd.DataFrame(timeline)
    if df.empty:
        return go.Figure().add_annotation(text="No timeline data available", showarrow=False)

    trade_events = df[df['event_type'] == 'trade_proposal']

    if trade_events.empty:
        return go.Figure().add_annotation(text="No trade events found", showarrow=False)

    trades_by_step = trade_events.groupby(
        'step').size().reset_index(name='trades')

    fig = px.bar(trades_by_step, x='step', y='trades',
                 title='Trades Completed by Simulation Step',
                 labels={'step': 'Simulation Step', 'trades': 'Number of Trades'})

    fig.update_layout(
        showlegend=False,
        height=400,
        title_font_size=16,
        title_x=0.5
    )

    return fig


def create_event_distribution_chart(timeline: List[Dict[str, Any]]) -> go.Figure:
    """Create pie chart showing distribution of event types."""
    df = pd.DataFrame(timeline)
    if df.empty:
        return go.Figure().add_annotation(text="No event data available", showarrow=False)

    event_counts = df['event_type'].value_counts()

    fig = px.pie(values=event_counts.values, names=event_counts.index,
                 title='Event Type Distribution')

    fig.update_layout(
        height=400,
        title_font_size=16,
        title_x=0.5
    )

    return fig


def main():
    """Main dashboard application."""
    st.set_page_config(
        page_title="Red Paperclip Hackathon Dashboard",
        page_icon="📎",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Header
    st.title("📎 Red Paperclip Hackathon Dashboard")
    st.markdown("**Real-time metrics from autonomous AI agent simulations**")
    st.markdown("---")

    # Load session data
    sessions = load_session_logs()

    if not sessions:
        st.error("No session logs found in simulation_logs/ directory")
        st.info(
            "Run a simulation first: `python run_hackathon_demo.py --agents 5 --steps 20`")
        return

    # Sidebar for session selection
    st.sidebar.title("📊 Session Selection")
    session_options = [
        f"{s['timestamp']} ({s['event_count']} events)" for s in sessions]
    selected_idx = st.sidebar.selectbox("Choose Session:", range(len(sessions)),
                                        format_func=lambda x: session_options[x])

    selected_session = sessions[selected_idx]
    metrics = analyze_session_metrics(selected_session['events'])

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Quick Stats:**")
    st.sidebar.metric("Total Events", metrics['total_events'])
    st.sidebar.metric("Active Agents", metrics['agents_active'])
    st.sidebar.metric("Session", selected_session['timestamp'])

    # Main metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("✅ Trades Completed", metrics['trades_completed'])

    with col2:
        st.metric("🤝 Coalitions Formed", metrics['coalitions_formed'])

    with col3:
        st.metric("⚡ Chaos Events", metrics['chaos_events'])

    with col4:
        st.metric("💸 x402 Payments", metrics['x402_payments'])

    # Payment success rate
    st.metric("📈 x402 Success Rate", f"{metrics['x402_success_rate']:.1f}%")

    st.markdown("---")

    # Charts row
    col1, col2 = st.columns(2)

    with col1:
        trade_chart = create_trade_timeline_chart(metrics['event_timeline'])
        st.plotly_chart(trade_chart, use_container_width=True)

    with col2:
        event_chart = create_event_distribution_chart(
            metrics['event_timeline'])
        st.plotly_chart(event_chart, use_container_width=True)

    # Payment receipts table
    if metrics['payment_receipts']:
        st.markdown("### 💸 Payment Receipts")
        payment_df = pd.DataFrame(metrics['payment_receipts'])
        payment_df['timestamp'] = pd.to_datetime(
            payment_df['timestamp']).dt.strftime('%H:%M:%S')
        payment_df['correlation_id'] = payment_df['correlation_id'].str[:8] + '...'

        st.dataframe(payment_df, use_container_width=True)

    # Recent persuasion pitches
    if metrics['recent_pitches']:
        st.markdown("### 🗣️ Recent Persuasion Pitches")

        for pitch in metrics['recent_pitches'][-5:]:  # Show last 5
            with st.expander(f"Pitch from {pitch['from_agent']} to {pitch['to_agent']} (Cost: {pitch['cost']})"):
                st.write(pitch['pitch'])
                st.caption(f"Timestamp: {pitch['timestamp']}")

    # Latest capsule snapshot
    if metrics['latest_capsule']:
        st.markdown("### 🧩 Latest Agent Capsule Snapshot")

        with st.expander("View Capsule Details"):
            capsule = metrics['latest_capsule']

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Agent Identity:**")
                st.write(f"**ID:** {capsule.get('agent_id', 'Unknown')}")
                st.write(
                    f"**Goal:** {capsule.get('goal', 'No goal specified')}")
                st.write(
                    f"**Wallet:** {capsule.get('wallet_address', 'No wallet')}")

            with col2:
                st.markdown("**Values & Tags:**")
                values = capsule.get('values', {})
                if values:
                    for key, value in values.items():
                        st.write(f"**{key.title()}:** {value}")

                tags = capsule.get('tags', [])
                if tags:
                    st.write(f"**Tags:** {', '.join(tags)}")

    # Debug information
    with st.expander("🔧 Debug Information"):
        st.markdown("**Session File:** " + selected_session['filename'])
        st.markdown(f"**Total Events:** {len(selected_session['events'])}")

        if st.checkbox("Show Raw Event Data"):
            st.json(selected_session['events'][-5:])  # Show last 5 events


if __name__ == "__main__":
    main()
