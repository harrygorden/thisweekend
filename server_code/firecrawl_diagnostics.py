"""
Firecrawl API Diagnostics Module

Tests Firecrawl API connectivity, authentication, and functionality
to help debug connection issues.
"""

import anvil.server
import anvil.http
import json
from . import api_helpers


@anvil.server.callable
def test_firecrawl_connection():
    """
    Test basic Firecrawl API connectivity and authentication.
    Tests with a known-good URL first.
    
    Returns:
        dict: Test results
    """
    results = {
        'timestamp': str(anvil.server.context.timestamp) if hasattr(anvil.server.context, 'timestamp') else 'unknown',
        'tests': {}
    }
    
    # Get API key
    try:
        api_key = api_helpers.get_api_key("FIRECRAWL_API_KEY")
        results['api_key_configured'] = True
        results['api_key_preview'] = f"{api_key[:10]}...{api_key[-4:]}" if len(api_key) > 14 else "***"
    except Exception as e:
        results['api_key_configured'] = False
        results['api_key_error'] = str(e)
        return results
    
    # Test 1: Simple test URL (firecrawl.dev - should always work)
    print("\n" + "="*60)
    print("TEST 1: Firecrawl with Known-Good URL")
    print("="*60)
    
    test_url = "https://firecrawl.dev"
    results['tests']['test_url'] = test_firecrawl_url(api_key, test_url, use_stealth=False)
    
    # Test 2: Target URL without stealth
    print("\n" + "="*60)
    print("TEST 2: Target URL without Stealth Mode")
    print("="*60)
    
    target_url = "https://ilovememphisblog.com/weekend"
    results['tests']['target_no_stealth'] = test_firecrawl_url(api_key, target_url, use_stealth=False)
    
    # Test 3: Target URL with stealth
    print("\n" + "="*60)
    print("TEST 3: Target URL with Stealth Mode")
    print("="*60)
    
    results['tests']['target_with_stealth'] = test_firecrawl_url(api_key, target_url, use_stealth=True)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for test_name, test_result in results['tests'].items():
        status = "✅ SUCCESS" if test_result['success'] else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not test_result['success']:
            print(f"  Error: {test_result.get('error', 'Unknown')}")
    
    return results


def test_firecrawl_url(api_key, url, use_stealth=False):
    """
    Test scraping a specific URL with Firecrawl.
    
    Args:
        api_key: Firecrawl API key
        url: URL to test
        use_stealth: Whether to use stealth mode
        
    Returns:
        dict: Test results
    """
    result = {
        'url': url,
        'stealth': use_stealth,
        'success': False
    }
    
    # Build request
    api_url = "https://api.firecrawl.dev/v1/scrape"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": url,
        "formats": ["markdown"]
    }
    
    if use_stealth:
        payload["stealth"] = True
        payload["timeout"] = 60000
    
    print(f"Testing URL: {url}")
    print(f"Stealth mode: {use_stealth}")
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Make request
        response = anvil.http.request(
            api_url,
            method="POST",
            json=payload,
            headers=headers,
            timeout=90
        )
        
        # Convert response
        response_text = response.get_bytes().decode('utf-8')
        response_json = json.loads(response_text)
        
        print(f"Response received: {len(response_text)} bytes")
        print(f"Response keys: {list(response_json.keys())}")
        
        # Check success
        if response_json.get('success'):
            result['success'] = True
            result['response_size'] = len(response_text)
            
            if 'data' in response_json:
                data = response_json['data']
                if 'markdown' in data:
                    result['markdown_size'] = len(data['markdown'])
                if 'metadata' in data:
                    result['metadata'] = data['metadata']
            
            print(f"✅ SUCCESS! Got {result.get('markdown_size', 0)} chars of markdown")
        else:
            result['success'] = False
            result['error'] = response_json.get('error', 'Unknown error')
            print(f"❌ Firecrawl returned error: {result['error']}")
        
    except anvil.http.HttpError as e:
        result['success'] = False
        result['http_status'] = e.status
        
        # Try to get error details
        try:
            if hasattr(e, 'content') and e.content:
                if hasattr(e.content, 'get_bytes'):
                    error_body = e.content.get_bytes().decode('utf-8')
                else:
                    error_body = str(e.content)
                
                error_json = json.loads(error_body)
                result['error'] = error_json.get('error', f'HTTP {e.status}')
                result['error_code'] = error_json.get('code', 'unknown')
                result['error_details'] = error_json
                
                print(f"❌ HTTP {e.status}: {result['error']}")
                print(f"Error code: {result['error_code']}")
                print(f"Full error: {json.dumps(error_json, indent=2)}")
        except:
            result['error'] = f'HTTP {e.status}'
            print(f"❌ HTTP Error {e.status} (no details)")
        
    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
        print(f"❌ Exception: {str(e)}")
    
    return result


@anvil.server.callable
def test_firecrawl_v0_endpoint():
    """
    Test Firecrawl v0 endpoint (older version).
    Sometimes v0 works when v1/v2 fail.
    
    Returns:
        dict: Test results
    """
    print("\n" + "="*60)
    print("TESTING FIRECRAWL v0 ENDPOINT")
    print("="*60)
    
    try:
        api_key = api_helpers.get_api_key("FIRECRAWL_API_KEY")
    except Exception as e:
        return {'success': False, 'error': str(e)}
    
    # v0 endpoint (legacy)
    api_url = "https://api.firecrawl.dev/v0/scrape"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": "https://ilovememphisblog.com/weekend",
        "pageOptions": {
            "onlyMainContent": True
        }
    }
    
    print(f"Testing v0 endpoint: {api_url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = anvil.http.request(
            api_url,
            method="POST",
            json=payload,
            headers=headers,
            timeout=90
        )
        
        response_text = response.get_bytes().decode('utf-8')
        response_json = json.loads(response_text)
        
        print(f"✅ v0 API responded!")
        print(f"Response keys: {list(response_json.keys())}")
        
        if response_json.get('success'):
            print(f"✅ v0 API WORKS!")
            return {
                'success': True,
                'version': 'v0',
                'content_size': len(response_json.get('data', {}).get('content', ''))
            }
        else:
            print(f"❌ v0 API error: {response_json.get('error')}")
            return {
                'success': False,
                'error': response_json.get('error')
            }
            
    except anvil.http.HttpError as e:
        print(f"❌ HTTP {e.status}")
        return {'success': False, 'error': f'HTTP {e.status}'}
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return {'success': False, 'error': str(e)}

