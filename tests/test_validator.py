#!/usr/bin/env python3
"""
Unit Tests for Metro Data Validator (US-202)

Tests the data validation pipeline module that validates metro network data
for errors and inconsistencies.
"""

import pytest
from pathlib import Path
from datetime import datetime
from src.graph.validator import (
    ValidationIssue,
    ValidationReport,
    MetroDataValidator,
    validate_metro_data
)


class TestValidationIssue:
    """Tests for ValidationIssue dataclass."""

    def test_create_validation_issue(self):
        """Test creating a validation issue."""
        issue = ValidationIssue(
            severity='error',
            category='connectivity',
            message='Graph is disconnected',
            details={'components': 2}
        )

        assert issue.severity == 'error'
        assert issue.category == 'connectivity'
        assert issue.message == 'Graph is disconnected'
        assert issue.details == {'components': 2}

    def test_create_issue_without_details(self):
        """Test creating issue without details."""
        issue = ValidationIssue(
            severity='warning',
            category='duplicates',
            message='Found duplicate connections'
        )

        assert issue.severity == 'warning'
        assert issue.details is None


class TestValidationReport:
    """Tests for ValidationReport dataclass."""

    @pytest.fixture
    def sample_report(self, tmp_path):
        """Create a sample validation report."""
        return ValidationReport(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data_files={
                'stations': tmp_path / 'stations.csv',
                'connections': tmp_path / 'connections.csv'
            }
        )

    def test_create_validation_report(self, sample_report):
        """Test creating a validation report."""
        assert sample_report.timestamp is not None
        assert len(sample_report.data_files) == 2
        assert len(sample_report.issues) == 0
        assert len(sample_report.stats) == 0

    def test_add_error(self, sample_report):
        """Test adding an error to report."""
        sample_report.add_error('connectivity', 'Graph is disconnected')

        assert len(sample_report.issues) == 1
        assert sample_report.issues[0].severity == 'error'
        assert sample_report.issues[0].category == 'connectivity'

    def test_add_warning(self, sample_report):
        """Test adding a warning to report."""
        sample_report.add_warning('duplicates', 'Found duplicate connections')

        assert len(sample_report.issues) == 1
        assert sample_report.issues[0].severity == 'warning'

    def test_add_info(self, sample_report):
        """Test adding info to report."""
        sample_report.add_info('connectivity', 'Graph is fully connected')

        assert len(sample_report.issues) == 1
        assert sample_report.issues[0].severity == 'info'

    def test_has_errors_with_errors(self, sample_report):
        """Test has_errors returns True when errors exist."""
        sample_report.add_error('test', 'Test error')

        assert sample_report.has_errors() is True

    def test_has_errors_without_errors(self, sample_report):
        """Test has_errors returns False when no errors exist."""
        sample_report.add_warning('test', 'Test warning')
        sample_report.add_info('test', 'Test info')

        assert sample_report.has_errors() is False

    def test_get_summary(self, sample_report):
        """Test getting summary counts."""
        sample_report.add_error('test', 'Error 1')
        sample_report.add_error('test', 'Error 2')
        sample_report.add_warning('test', 'Warning 1')
        sample_report.add_info('test', 'Info 1')

        summary = sample_report.get_summary()

        assert summary['error'] == 2
        assert summary['warning'] == 1
        assert summary['info'] == 1


class TestMetroDataValidator:
    """Tests for MetroDataValidator class."""

    @pytest.fixture
    def validator(self):
        """Create a validator instance."""
        return MetroDataValidator()

    @pytest.fixture
    def sample_stations_csv(self, tmp_path):
        """Create a sample stations CSV file."""
        csv_path = tmp_path / "stations.csv"
        content = """station_id,station_name,line_code,latitude,longitude,operational_status
NS1,Jurong East,NS,1.3332,103.7421,operational
NS2,Bukit Batok,NS,1.3490,103.7499,operational
EW1,Pasir Ris,EW,1.3730,103.9493,operational
"""
        csv_path.write_text(content)
        return csv_path

    @pytest.fixture
    def sample_connections_csv(self, tmp_path):
        """Create a sample connections CSV file."""
        csv_path = tmp_path / "connections.csv"
        content = """connection_id,from_station_id,to_station_id,connection_type,travel_time_minutes,distance_meters,line_code
1,NS1,NS2,train,2.5,1234,NS
2,NS2,NS1,train,2.5,1234,NS
3,NS2,EW1,walk_transfer,3.0,150,NA
"""
        csv_path.write_text(content)
        return csv_path

    @pytest.fixture
    def sample_lines_csv(self, tmp_path):
        """Create a sample lines CSV file."""
        csv_path = tmp_path / "lines.csv"
        content = """line_code,line_name,line_type,color_hex,first_station,last_station,num_stations,operational_status
NS,North South Line,MRT,#D42E12,NS1,NS28,27,operational
EW,East West Line,MRT,#009645,EW1,EW33,35,operational
"""
        csv_path.write_text(content)
        return csv_path

    def test_validator_initialization(self, validator):
        """Test validator initializes correctly."""
        assert validator.report is None
        assert len(validator.stations) == 0
        assert len(validator.connections) == 0
        assert len(validator.lines) == 0

    def test_validate_with_valid_data(self, validator, sample_stations_csv,
                                     sample_connections_csv, sample_lines_csv):
        """Test validation with valid data."""
        report = validator.validate(
            sample_stations_csv,
            sample_connections_csv,
            sample_lines_csv
        )

        assert report is not None
        assert isinstance(report, ValidationReport)
        # Should have at least the connectivity info message
        assert any(issue.severity == 'info' for issue in report.issues)

    def test_validate_missing_file(self, validator, tmp_path):
        """Test validation with missing file."""
        missing_path = tmp_path / "nonexistent.csv"

        report = validator.validate(
            missing_path,
            missing_path,
            None
        )

        assert report.has_errors() is True
        assert any('file_missing' in issue.category for issue in report.issues)

    def test_load_data(self, validator, sample_stations_csv,
                       sample_connections_csv, sample_lines_csv):
        """Test loading data from CSV files."""
        validator.report = ValidationReport(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data_files={}
        )

        validator._load_data(
            sample_stations_csv,
            sample_connections_csv,
            sample_lines_csv
        )

        assert len(validator.stations) == 3
        assert len(validator.connections) == 3
        assert len(validator.lines) == 2

    def test_validate_data_integrity_valid(self, validator, sample_stations_csv,
                                          sample_connections_csv):
        """Test data integrity validation with valid data."""
        validator.report = ValidationReport(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data_files={}
        )
        validator._load_data(sample_stations_csv, sample_connections_csv, None)

        validator._validate_data_integrity()

        assert not any(issue.category == 'data_integrity'
                      for issue in validator.report.issues)

    def test_validate_station_references_valid(self, validator, sample_stations_csv,
                                              sample_connections_csv):
        """Test station reference validation with valid data."""
        validator.report = ValidationReport(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data_files={}
        )
        validator._load_data(sample_stations_csv, sample_connections_csv, None)

        validator._validate_station_references()

        assert not any(issue.category == 'missing_references'
                      for issue in validator.report.issues)

    def test_validate_station_references_invalid(self, validator, sample_stations_csv,
                                                tmp_path):
        """Test station reference validation with invalid references."""
        # Create connections with invalid station IDs
        invalid_conn_csv = tmp_path / "invalid_connections.csv"
        content = """connection_id,from_station_id,to_station_id,connection_type,travel_time_minutes,distance_meters,line_code
1,NS1,NS99,train,2.5,1234,NS
"""
        invalid_conn_csv.write_text(content)

        validator.report = ValidationReport(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data_files={}
        )
        validator._load_data(sample_stations_csv, invalid_conn_csv, None)

        validator._validate_station_references()

        assert any(issue.category == 'missing_references'
                  for issue in validator.report.issues)

    def test_validate_travel_times_valid(self, validator, sample_stations_csv,
                                        sample_connections_csv):
        """Test travel time validation with valid data."""
        validator.report = ValidationReport(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data_files={}
        )
        validator._load_data(sample_stations_csv, sample_connections_csv, None)

        validator._validate_travel_times()

        assert not any(issue.category == 'invalid_travel_times'
                      for issue in validator.report.issues)

    def test_validate_travel_times_invalid(self, validator, sample_stations_csv,
                                          tmp_path):
        """Test travel time validation with invalid times."""
        # Create connections with invalid travel times
        invalid_conn_csv = tmp_path / "invalid_connections.csv"
        content = """connection_id,from_station_id,to_station_id,connection_type,travel_time_minutes,distance_meters,line_code
1,NS1,NS2,train,-2.5,1234,NS
2,NS2,NS1,train,0,1234,NS
"""
        invalid_conn_csv.write_text(content)

        validator.report = ValidationReport(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data_files={}
        )
        validator._load_data(sample_stations_csv, invalid_conn_csv, None)

        validator._validate_travel_times()

        assert any(issue.category == 'invalid_travel_times'
                  for issue in validator.report.issues)

    def test_validate_distances_valid(self, validator, sample_stations_csv,
                                     sample_connections_csv):
        """Test distance validation with valid data."""
        validator.report = ValidationReport(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data_files={}
        )
        validator._load_data(sample_stations_csv, sample_connections_csv, None)

        validator._validate_distances()

        # Should not have errors (warnings for large distances are OK)
        assert not any(issue.severity == 'error' and
                      issue.category == 'invalid_distances'
                      for issue in validator.report.issues)

    def test_validate_distances_invalid(self, validator, sample_stations_csv,
                                       tmp_path):
        """Test distance validation with invalid distances."""
        # Create connections with invalid distances
        invalid_conn_csv = tmp_path / "invalid_connections.csv"
        content = """connection_id,from_station_id,to_station_id,connection_type,travel_time_minutes,distance_meters,line_code
1,NS1,NS2,train,2.5,-100,NS
"""
        invalid_conn_csv.write_text(content)

        validator.report = ValidationReport(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data_files={}
        )
        validator._load_data(sample_stations_csv, invalid_conn_csv, None)

        validator._validate_distances()

        assert any(issue.category == 'invalid_distances'
                  for issue in validator.report.issues)

    def test_detect_duplicate_connections(self, validator, sample_stations_csv,
                                         tmp_path):
        """Test duplicate connection detection."""
        # Create connections with duplicates
        dup_conn_csv = tmp_path / "dup_connections.csv"
        content = """connection_id,from_station_id,to_station_id,connection_type,travel_time_minutes,distance_meters,line_code
1,NS1,NS2,train,2.5,1234,NS
2,NS1,NS2,train,2.5,1234,NS
"""
        dup_conn_csv.write_text(content)

        validator.report = ValidationReport(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data_files={}
        )
        validator._load_data(sample_stations_csv, dup_conn_csv, None)

        validator._detect_duplicate_connections()

        assert any(issue.category == 'duplicate_connections'
                  for issue in validator.report.issues)

    def test_validate_graph_connectivity_connected(self, validator,
                                                   sample_stations_csv,
                                                   sample_connections_csv):
        """Test graph connectivity validation with connected graph."""
        validator.report = ValidationReport(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data_files={}
        )
        validator._load_data(sample_stations_csv, sample_connections_csv, None)

        validator._validate_graph_connectivity()

        # Should have info message about connectivity
        assert any(issue.severity == 'info' and
                  issue.category == 'connectivity'
                  for issue in validator.report.issues)

    def test_validate_graph_connectivity_disconnected(self, validator,
                                                     tmp_path):
        """Test graph connectivity validation with disconnected graph."""
        # Create disconnected stations
        stations_csv = tmp_path / "stations.csv"
        stations_content = """station_id,station_name,line_code,latitude,longitude,operational_status
NS1,Jurong East,NS,1.3332,103.7421,operational
NS2,Bukit Batok,NS,1.3490,103.7499,operational
EW1,Pasir Ris,EW,1.3730,103.9493,operational
"""
        stations_csv.write_text(stations_content)

        # Create connections that leave EW1 disconnected
        conn_csv = tmp_path / "connections.csv"
        conn_content = """connection_id,from_station_id,to_station_id,connection_type,travel_time_minutes,distance_meters,line_code
1,NS1,NS2,train,2.5,1234,NS
2,NS2,NS1,train,2.5,1234,NS
"""
        conn_csv.write_text(conn_content)

        validator.report = ValidationReport(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data_files={}
        )
        validator._load_data(stations_csv, conn_csv, None)

        validator._validate_graph_connectivity()

        assert any(issue.category == 'disconnected_graph'
                  for issue in validator.report.issues)

    def test_collect_statistics(self, validator, sample_stations_csv,
                                sample_connections_csv, sample_lines_csv):
        """Test statistics collection."""
        validator.report = ValidationReport(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data_files={}
        )
        validator._load_data(sample_stations_csv, sample_connections_csv,
                           sample_lines_csv)

        validator._collect_statistics()

        assert validator.report.stats['num_stations'] == 3
        assert validator.report.stats['num_connections'] == 3
        assert validator.report.stats['num_lines'] == 2
        assert 'connection_types' in validator.report.stats

    def test_count_connection_types(self, validator, sample_stations_csv,
                                    sample_connections_csv):
        """Test counting connections by type."""
        validator.report = ValidationReport(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data_files={}
        )
        validator._load_data(sample_stations_csv, sample_connections_csv, None)

        counts = validator._count_connection_types()

        assert counts['train'] == 2
        assert counts['walk_transfer'] == 1


class TestValidateMetroDataFunction:
    """Tests for validate_metro_data convenience function."""

    @pytest.fixture
    def sample_data_dir(self, tmp_path):
        """Create a sample data directory with CSV files."""
        # Create stations.csv
        stations_csv = tmp_path / "stations.csv"
        stations_content = """station_id,station_name,line_code,latitude,longitude,operational_status
NS1,Jurong East,NS,1.3332,103.7421,operational
NS2,Bukit Batok,NS,1.3490,103.7499,operational
"""
        stations_csv.write_text(stations_content)

        # Create connections.csv
        connections_csv = tmp_path / "connections.csv"
        connections_content = """connection_id,from_station_id,to_station_id,connection_type,travel_time_minutes,distance_meters,line_code
1,NS1,NS2,train,2.5,1234,NS
2,NS2,NS1,train,2.5,1234,NS
"""
        connections_csv.write_text(connections_content)

        # Create lines.csv
        lines_csv = tmp_path / "lines.csv"
        lines_content = """line_code,line_name,line_type,color_hex,first_station,last_station,num_stations,operational_status
NS,North South Line,MRT,#D42E12,NS1,NS28,27,operational
"""
        lines_csv.write_text(lines_content)

        return tmp_path

    def test_validate_metro_data_with_defaults(self, sample_data_dir):
        """Test validate_metro_data with default file names."""
        report = validate_metro_data(sample_data_dir)

        assert report is not None
        assert isinstance(report, ValidationReport)
        assert 'stations' in report.data_files
        assert 'connections' in report.data_files
        assert 'lines' in report.data_files

    def test_validate_metro_data_with_custom_names(self, tmp_path):
        """Test validate_metro_data with custom file names."""
        # Create custom named files
        stations_csv = tmp_path / "my_stations.csv"
        stations_content = """station_id,station_name,line_code,latitude,longitude,operational_status
NS1,Jurong East,NS,1.3332,103.7421,operational
"""
        stations_csv.write_text(stations_content)

        connections_csv = tmp_path / "my_connections.csv"
        connections_content = """connection_id,from_station_id,to_station_id,connection_type,travel_time_minutes,distance_meters,line_code
"""
        connections_csv.write_text(connections_content)

        lines_csv = tmp_path / "my_lines.csv"
        lines_content = """line_code,line_name,line_type,color_hex,first_station,last_station,num_stations,operational_status
"""
        lines_csv.write_text(lines_content)

        report = validate_metro_data(
            tmp_path,
            stations_file='my_stations.csv',
            connections_file='my_connections.csv',
            lines_file='my_lines.csv'
        )

        assert report is not None

    def test_validate_metro_data_without_lines(self, tmp_path):
        """Test validate_metro_data when lines file doesn't exist."""
        # Create only stations and connections
        stations_csv = tmp_path / "stations.csv"
        stations_content = """station_id,station_name,line_code,latitude,longitude,operational_status
NS1,Jurong East,NS,1.3332,103.7421,operational
"""
        stations_csv.write_text(stations_content)

        connections_csv = tmp_path / "connections.csv"
        connections_content = """connection_id,from_station_id,to_station_id,connection_type,travel_time_minutes,distance_meters,line_code
"""
        connections_csv.write_text(connections_content)

        report = validate_metro_data(tmp_path)

        assert report is not None
        # Should work even without lines file


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
