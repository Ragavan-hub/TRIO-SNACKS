# Vercel Deployment Guide

## Important Notes for Vercel Deployment

⚠️ **Vercel is a serverless platform with limitations:**

1. **Database**: SQLite files are not persistent on Vercel. You need to use an external database:
   - Set `DATABASE_URL` environment variable to a PostgreSQL/MySQL database
   - Recommended: Use services like Supabase, PlanetScale, or Railway for database

2. **File Storage**: Uploaded files (images, logos) are not persistent in `/tmp`:
   - Files in `/tmp` are deleted after function execution
   - Consider using cloud storage (AWS S3, Cloudinary, etc.)
   - Or use Vercel Blob Storage

3. **Environment Variables**: Set these in Vercel dashboard:
   - `SECRET_KEY`: A secure random string
   - `DATABASE_URL`: Your database connection string (required!)

## Setup Steps

1. **Set Environment Variables in Vercel:**
   ```
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   ```

2. **Deploy to Vercel:**
   ```bash
   npm i -g vercel
   vercel
   ```

3. **For Production Database:**
   - Use PostgreSQL or MySQL
   - Update `DATABASE_URL` in Vercel environment variables
   - The app will automatically use it

## Alternative: Use Railway/Render for Better Compatibility

This Flask app with SQLite and file uploads works better on:
- **Railway**: https://railway.app
- **Render**: https://render.com
- **Heroku**: https://heroku.com

These platforms provide persistent file storage and better support for Flask apps.

## Current Vercel Configuration

- Entry point: `api/index.py`
- Static files: Served from `/static/`
- Database: Uses `/tmp/database.db` (not persistent - use external DB!)
- File uploads: Stored in `/tmp/` (not persistent - use cloud storage!)

