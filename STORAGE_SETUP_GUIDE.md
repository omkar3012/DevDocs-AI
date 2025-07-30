# Storage Setup Guide for DevDocs AI

This guide will help you set up the Supabase storage bucket that's required for DevDocs AI to function properly.

## The Problem

You're seeing this error in the debug output:
```
📦 Storage Bucket Check:
   ❌ api-docs bucket not found
   Available buckets: []
```

This means the `api-docs` storage bucket hasn't been created in your Supabase project yet.

## Solution: Manual Bucket Creation

Since Supabase storage buckets must be created through the dashboard (not via SQL or API), follow these steps:

### Step 1: Create the Storage Bucket

1. **Go to your Supabase Dashboard**
   - Navigate to your project at https://supabase.com/dashboard
   - Select your DevDocs AI project

2. **Navigate to Storage**
   - Click on **Storage** in the left sidebar
   - Click on **Buckets**

3. **Create New Bucket**
   - Click **Create a new bucket**
   - Set the following:
     - **Name**: `api-docs` (exactly this name)
     - **Public bucket**: **UNCHECKED** (keep it private for security)
   - Click **Create bucket**

### Step 2: Set Up Storage Policies

After creating the bucket, you need to set up access policies:

1. **Go to Storage Policies**
   - In the Storage section, click on **Policies**
   - Select the `api-docs` bucket from the dropdown

2. **Create Upload Policy**
   - Click **New Policy**
   - Set the following:
     - **Policy Name**: `Allow authenticated uploads`
     - **Allowed operation**: `INSERT`
     - **Target roles**: `authenticated`
     - **Policy definition**: `true`
   - Click **Review** then **Save policy**

3. **Create Download Policy**
   - Click **New Policy**
   - Set the following:
     - **Policy Name**: `Allow authenticated downloads`
     - **Allowed operation**: `SELECT`
     - **Target roles**: `authenticated`
     - **Policy definition**: `true`
   - Click **Review** then **Save policy**

4. **Create Delete Policy**
   - Click **New Policy**
   - Set the following:
     - **Policy Name**: `Allow authenticated deletes`
     - **Allowed operation**: `DELETE`
     - **Target roles**: `authenticated`
     - **Policy definition**: `true`
   - Click **Review** then **Save policy**

### Step 3: Verify Setup

Run the storage setup script to verify everything is working:

```bash
cd backend
python simple_storage_setup.py
```

You should see:
```
✅ api-docs bucket found
✅ Bucket access confirmed
```

## Alternative: Advanced Security Policies

If you want more granular security (recommended for production), use these policies instead:

### Policy 1: Upload Access
- **Name**: `Users can upload their own files`
- **Operation**: `INSERT`
- **Roles**: `authenticated`
- **Definition**: `auth.uid()::text = (storage.foldername(name))[1]`

### Policy 2: Download Access
- **Name**: `Users can view their own files`
- **Operation**: `SELECT`
- **Roles**: `authenticated`
- **Definition**: `auth.uid()::text = (storage.foldername(name))[1]`

### Policy 3: Delete Access
- **Name**: `Users can delete their own files`
- **Operation**: `DELETE`
- **Roles**: `authenticated`
- **Definition**: `auth.uid()::text = (storage.foldername(name))[1]`

## Troubleshooting

### Error: "must be owner of table objects"

This error occurs when trying to run SQL commands on storage tables. **Solution**: Don't use SQL for storage setup. Use the Supabase dashboard instead.

### Error: "Bucket not found"

**Solution**: Make sure you created the bucket with the exact name `api-docs` (with the hyphen).

### Error: "Access denied"

**Solution**: Check that you've created the storage policies correctly and that your service role key has the necessary permissions.

### Error: "Policy creation failed"

**Solution**: Try the simpler policies first (`true` for all operations), then upgrade to more secure policies later.

## Testing the Setup

After setting up the storage bucket, test it by:

1. **Running the debug script**:
   ```bash
   cd backend
   python debug_pipeline.py
   ```

2. **Uploading a test document** through the frontend

3. **Checking the storage bucket** in the Supabase dashboard to see if files appear

## Next Steps

Once the storage bucket is working:

1. ✅ Storage bucket created
2. ✅ Storage policies configured
3. ✅ Debug script shows bucket access
4. ✅ Document uploads work
5. ✅ Document processing pipeline works

Your DevDocs AI application should now be fully functional! 