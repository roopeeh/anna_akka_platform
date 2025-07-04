import json
import os
import boto3
from datetime import datetime, timedelta
import sys
sys.path.append('..')
from constants import ORDERS_TABLE, PRODUCTS_TABLE, STORES_TABLE, ERROR_CODES, STATUS_CODES, CORS_HEADERS, ANALYTICS_PERIODS

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table(os.environ[ORDERS_TABLE])
products_table = dynamodb.Table(os.environ[PRODUCTS_TABLE])
stores_table = dynamodb.Table(os.environ[STORES_TABLE])

def get_sales_analytics(store_id, period='month'):
    """Get sales analytics for a store"""
    try:
        # Calculate date range based on period
        end_date = datetime.utcnow()
        if period == ANALYTICS_PERIODS['DAY']:
            start_date = end_date - timedelta(days=1)
        elif period == ANALYTICS_PERIODS['WEEK']:
            start_date = end_date - timedelta(weeks=1)
        elif period == ANALYTICS_PERIODS['MONTH']:
            start_date = end_date - timedelta(days=30)
        elif period == ANALYTICS_PERIODS['YEAR']:
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)  # Default to month
        
        # Query orders for the store in the date range
        response = orders_table.query(
            IndexName='store_id_index',
            KeyConditionExpression='store_id = :store_id',
            FilterExpression='#created_at BETWEEN :start_date AND :end_date',
            ExpressionAttributeValues={
                ':store_id': store_id,
                ':start_date': start_date.isoformat(),
                ':end_date': end_date.isoformat()
            },
            ExpressionAttributeNames={
                '#created_at': 'created_at'
            }
        )
        
        orders = response.get('Items', [])
        
        # Calculate analytics
        total_orders = len(orders)
        total_revenue = sum(order.get('total_amount', 0) for order in orders)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Status breakdown
        status_counts = {}
        for order in orders:
            status = order.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'period': period,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'average_order_value': avg_order_value,
            'status_breakdown': status_counts,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }
        
    except Exception as e:
        raise e

def get_product_analytics(store_id, period='month'):
    """Get product analytics for a store"""
    try:
        # Get all products for the store
        response = products_table.query(
            IndexName='store_id_index',
            KeyConditionExpression='store_id = :store_id',
            ExpressionAttributeValues={':store_id': store_id}
        )
        
        products = response.get('Items', [])
        
        # Calculate product analytics
        total_products = len(products)
        products_in_stock = len([p for p in products if p.get('stock', 0) > 0])
        products_out_of_stock = total_products - products_in_stock
        
        # Price analysis
        prices = [p.get('price', 0) for p in products if p.get('price')]
        avg_price = sum(prices) / len(prices) if prices else 0
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0
        
        return {
            'total_products': total_products,
            'products_in_stock': products_in_stock,
            'products_out_of_stock': products_out_of_stock,
            'price_analysis': {
                'average_price': avg_price,
                'min_price': min_price,
                'max_price': max_price
            }
        }
        
    except Exception as e:
        raise e

def handler(event, context):
    """Main Lambda handler for analytics"""
    try:
        # Parse the request
        path = event.get('requestContext', {}).get('http', {}).get('path', '')
        method = event.get('requestContext', {}).get('http', {}).get('method', '')
        
        # Parse query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        
        # Route based on path and method
        if path.startswith('/analytics/sales/') and method == 'GET':
            store_id = path.split('/')[-1]
            period = query_params.get('period', 'month')
            return handle_sales_analytics(store_id, period)
        elif path.startswith('/analytics/products/') and method == 'GET':
            store_id = path.split('/')[-1]
            period = query_params.get('period', 'month')
            return handle_product_analytics(store_id, period)
        else:
            return {
                'statusCode': STATUS_CODES['NOT_FOUND'],
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'error': {
                        'code': ERROR_CODES['NOT_FOUND'],
                        'message': 'Endpoint not found'
                    }
                })
            }
            
    except Exception as e:
        return {
            'statusCode': STATUS_CODES['INTERNAL_ERROR'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': ERROR_CODES['INTERNAL_ERROR'],
                    'message': str(e)
                }
            })
        }

def handle_sales_analytics(store_id, period):
    """Handle GET /analytics/sales/{store_id}"""
    try:
        # In a real app, you'd verify the user has access to this store
        analytics = get_sales_analytics(store_id, period)
        
        return {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'analytics': analytics})
        }
    except Exception as e:
        return {
            'statusCode': STATUS_CODES['INTERNAL_ERROR'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': ERROR_CODES['INTERNAL_ERROR'],
                    'message': str(e)
                }
            })
        }

def handle_product_analytics(store_id, period):
    """Handle GET /analytics/products/{store_id}"""
    try:
        # In a real app, you'd verify the user has access to this store
        analytics = get_product_analytics(store_id, period)
        
        return {
            'statusCode': STATUS_CODES['OK'],
            'headers': CORS_HEADERS,
            'body': json.dumps({'analytics': analytics})
        }
    except Exception as e:
        return {
            'statusCode': STATUS_CODES['INTERNAL_ERROR'],
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': {
                    'code': ERROR_CODES['INTERNAL_ERROR'],
                    'message': str(e)
                }
            })
        } 