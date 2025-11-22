import pytest
from app.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_no_credentials(mocker, client):
    """Test home page when AWS credentials are missing (clients return None)."""
    mocker.patch('app.app.get_aws_clients', return_value=(None, None))
    
    response = client.get('/')
    assert response.status_code == 500
    assert b"Error: Boto3 clients not initialized" in response.data

def test_home_success(mocker, client):
    """Test home page with mocked AWS data."""
    # Mock EC2 client
    mock_ec2 = mocker.Mock()
    mock_ec2.describe_instances.return_value = {
        "Reservations": [{
            "Instances": [{
                "InstanceId": "i-1234567890abcdef0",
                "State": {"Name": "running"},
                "InstanceType": "t2.micro",
                "PublicIpAddress": "1.2.3.4"
            }]
        }]
    }
    mock_ec2.describe_vpcs.return_value = {
        "Vpcs": [{"VpcId": "vpc-123", "CidrBlock": "10.0.0.0/16"}]
    }
    mock_ec2.describe_images.return_value = {
        "Images": [{"ImageId": "ami-123", "Name": "MyAMI"}]
    }

    # Mock ELB client
    mock_elb = mocker.Mock()
    mock_elb.describe_load_balancers.return_value = {
        "LoadBalancers": [{"LoadBalancerName": "my-lb", "DNSName": "my-lb.aws.com"}]
    }

    mocker.patch('app.app.get_aws_clients', return_value=(mock_ec2, mock_elb))

    response = client.get('/')
    assert response.status_code == 200
    assert b"i-1234567890abcdef0" in response.data
    assert b"vpc-123" in response.data
    assert b"my-lb" in response.data
    assert b"MyAMI" in response.data

def test_home_aws_error(mocker, client):
    """Test home page when AWS call fails."""
    mock_ec2 = mocker.Mock()
    mock_ec2.describe_instances.side_effect = Exception("AWS Error")
    
    # We need to return a valid client object that raises an exception when called
    mocker.patch('app.app.get_aws_clients', return_value=(mock_ec2, mocker.Mock()))

    response = client.get('/')
    assert response.status_code == 500
    assert b"Error fetching AWS data" in response.data
