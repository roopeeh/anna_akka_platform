# Anna Akka Platform - Modular Infrastructure

## 🏗️ New Modular Structure

The Pulumi infrastructure has been refactored into a modular structure to improve maintainability and reduce complexity.

### 📁 File Structure

```
anna_akka_platform/
├── __main__.py                    # Main entry point (now much smaller!)
├── infrastructure/                 # Modular infrastructure components
│   ├── __init__.py               # Package initialization
│   ├── database.py               # DynamoDB tables
│   ├── lambda_functions.py       # Lambda functions
│   └── api_gateway.py           # API Gateway and routes
├── deploy_modular.py             # Deployment helper script
└── MODULAR_STRUCTURE_README.md   # This file
```

### 🔧 Benefits of Modular Structure

1. **Easier Maintenance**: Each component is in its own file
2. **Better Organization**: Related resources are grouped together
3. **Faster Deployments**: Smaller files process faster
4. **Reduced Conflicts**: Less chance of merge conflicts
5. **Better Readability**: Clear separation of concerns

### 🚀 How to Deploy

#### Option 1: Using the Deployment Script (Recommended)
```bash
python deploy_modular.py
```

This will give you a menu with options:
- Preview changes
- Deploy infrastructure
- Destroy infrastructure
- Show current stack

#### Option 2: Direct Pulumi Commands
```bash
# Preview changes
pulumi preview

# Deploy
pulumi up --yes

# Destroy
pulumi destroy --yes
```

### 📋 What Each Module Does

#### `infrastructure/database.py`
- Creates all DynamoDB tables
- Defines table schemas and indexes
- Handles table naming and tagging

#### `infrastructure/lambda_functions.py`
- Creates all Lambda functions
- Sets up IAM roles and policies
- Configures environment variables
- Handles Lambda packaging

#### `infrastructure/api_gateway.py`
- Creates API Gateway
- Sets up integrations with Lambda functions
- Defines all API routes
- Handles CORS configuration

#### `__main__.py`
- Orchestrates all modules
- Imports and calls module functions
- Defines outputs
- Much cleaner and easier to understand

### 🔄 Migration from Old Structure

The new structure is **backward compatible**. Your existing:
- Lambda functions remain unchanged
- API endpoints remain the same
- Database tables keep their names
- All outputs are preserved

### ⚠️ Important Notes

1. **No Breaking Changes**: All existing functionality is preserved
2. **Same Resources**: Same AWS resources, just organized differently
3. **Faster Processing**: Smaller files mean faster Pulumi operations
4. **Better Error Handling**: Easier to identify and fix issues

### 🛠️ Making Changes

#### Adding a New Lambda Function
1. Edit `infrastructure/lambda_functions.py`
2. Add your function to `create_all_lambda_functions()`
3. Add corresponding routes in `infrastructure/api_gateway.py`

#### Adding a New Database Table
1. Edit `infrastructure/database.py`
2. Add your table definition
3. Update environment variables in `lambda_functions.py`

#### Adding New API Routes
1. Edit `infrastructure/api_gateway.py`
2. Add your route to `create_routes()`
3. Ensure corresponding Lambda integration exists

### 📊 Monitoring and Debugging

#### Check Current Stack
```bash
pulumi stack
```

#### View Outputs
```bash
pulumi stack output
```

#### View Resource Details
```bash
pulumi stack --show-urns
```

### 🎯 Next Steps

1. **Test the new structure**: Run `python deploy_modular.py` and choose option 1 (preview)
2. **Deploy if satisfied**: Choose option 2 to deploy
3. **Run your tests**: Verify all functionality works as expected
4. **Clean up old files**: Once confirmed working, you can remove the old monolithic `__main__.py`

### 🆘 Troubleshooting

#### Common Issues

1. **Import Errors**: Ensure `infrastructure/__init__.py` exists
2. **Module Not Found**: Check that all files are in the correct locations
3. **Deployment Failures**: Use `pulumi preview` first to catch issues

#### Getting Help

- Check the deployment script output for specific errors
- Use `pulumi logs` to see detailed deployment logs
- Review the modular structure if imports fail

---

**🎉 Congratulations!** Your infrastructure is now much more maintainable and easier to work with. 