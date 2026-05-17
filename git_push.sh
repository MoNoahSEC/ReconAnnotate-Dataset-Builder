#!/usr/bin/env bash

echo "🚀 Initializing Git repository for Noah ReconAnnotate Pro..."

# Initialize git if not already done
if [ ! -d ".git" ]; then
    git init
fi

# Add all files
git add .

# Commit
git commit -m "Initial commit of Noah ReconAnnotate Pro - Premium AI Dataset Builder"

# Rename branch
git branch -M main

# Add remote (remove if already exists to avoid errors)
git remote remove origin 2>/dev/null
git remote add origin https://github.com/MoNoahSEC/ReconAnnotate-Dataset-Builder.git

echo "📦 Pushing code to GitHub..."
git push -u origin main

echo "✅ Push completed! Visit: https://github.com/MoNoahSEC/ReconAnnotate-Dataset-Builder"
