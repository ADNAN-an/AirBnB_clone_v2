#!/usr/bin/python3
"""Initialization script for the models directory."""

from models.engine.file_storage import FileStorage

# Initialize storage
storage = FileStorage()
storage.reload()
