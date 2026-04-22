"""
Basic import tests for module verification.
"""

def test_module_import():
    """Test that the module can be imported."""
    import socratic_nexus
    assert socratic_nexus is not None

def test_main_exports():
    """Test that main exports are available."""
    from socratic_nexus import ClaudeClient
    assert ClaudeClient is not None
