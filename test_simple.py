#!/usr/bin/env python
"""
Test simple pour vérifier le middleware
"""
import os
import sys
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GenEX.settings')
django.setup()

from users.middleware import AdminAccessMiddleware

# Test du middleware
middleware = AdminAccessMiddleware(lambda req: None)

print("Test du middleware AdminAccessMiddleware...")
print("Paths autorises pour les admins:")
for path in middleware.allowed_paths:
    print(f"  - {path}")

print("\nPaths restreints pour les admins:")
for path in middleware.restricted_paths:
    print(f"  - {path}")

print("\nVerification:")
print(f"/courses/admin/ est-il autorise? {'/courses/admin/' in middleware.allowed_paths}")
print(f"/courses/ est-il restreint? {any('/courses/admin/'.startswith(p) for p in middleware.restricted_paths)}")
