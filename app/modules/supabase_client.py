"""Supabase client initialization and connection management."""
import streamlit as st
from supabase import create_client, Client
from typing import Optional


@st.cache_resource
def init_supabase() -> Client:
    """
    Initialize Supabase client with credentials from Streamlit secrets.
    Uses st.cache_resource to maintain a single connection instance.
    
    Returns:
        Client: Authenticated Supabase client
    """
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except KeyError as e:
        st.error(f"Missing Supabase configuration: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Failed to initialize Supabase: {e}")
        st.stop()


def get_supabase_client() -> Client:
    """Get the cached Supabase client instance."""
    return init_supabase()