# Company Route Slug Fix

Production issue: `/companies/microsoft`, `/companies/nvidia`, and `/companies/alphabet` rendered the fallback OpenAI company when the backend did not resolve the route segment as a company slug.

Fix:

- Frontend dynamic company routes pass the requested slug through to the API.
- Frontend fallback lookup matches by `id` or `slug`.
- Frontend detail pages render a 404 state when an entity is missing instead of falling back to the first company.
- Backend company detail and metrics routes resolve companies by UUID or active slug.
- Seed and fallback data include Alphabet so `/companies/alphabet` has a valid company record.

Verified routes:

- `/companies/microsoft`
- `/companies/nvidia`
- `/companies/alphabet`
