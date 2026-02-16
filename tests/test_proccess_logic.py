import pytest
from unittest.mock import MagicMock, patch
from src.core.proccess import run_massive_query_process


@patch('src.core.proccess.get_gre_batch')
@patch('src.core.proccess.get_gre_by_ruc_and_serie')
@patch('src.core.proccess.StorageService')
def test_run_massive_query_process(mock_storage_service, mock_get_detail, mock_get_batch):
    # Setup mocks
    mock_token = "fake_token"
    mock_receptor = "20000000001"
    mock_emitters = ["20100000001"]

    # Mock Batch Response
    mock_item = MagicMock()
    mock_item.rucEmisor = "20100000001"
    mock_item.codCpe = "09"
    mock_item.numSerie = "T001"
    mock_item.numCpe = 1

    mock_batch = MagicMock()
    mock_batch.items = [mock_item]
    mock_get_batch.return_value = mock_batch

    # Mock Detail and Storage
    mock_detail = MagicMock()
    mock_get_detail.return_value = mock_detail

    storage_instance = mock_storage_service.return_value

    # Run process
    run_massive_query_process(mock_token, mock_receptor, mock_emitters)

    # Assertions
    mock_get_batch.assert_called_once()
    mock_get_detail.assert_called_once()
    storage_instance.store_gre.assert_called_with(mock_detail)


@patch('src.core.proccess.get_gre_batch')
def test_run_massive_query_process_no_items(mock_get_batch):
    mock_get_batch.return_value = None

    # Setup
    mock_token = "fake_token"
    mock_receptor = "20000000001"
    mock_emitters = ["20100000001"]

    with patch('src.core.proccess.StorageService') as mock_storage:
        run_massive_query_process(mock_token, mock_receptor, mock_emitters)

        # Should not call store_gre if batch is empty
        mock_storage.return_value.store_gre.assert_not_called()
