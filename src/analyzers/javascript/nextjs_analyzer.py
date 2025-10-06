#!/usr/bin/env python3
"""
Next.js Code Analyzer - detects Next.js-specific anti-patterns.

This analyzer focuses on Next.js framework-specific issues:
- React Server Components misuse
- Image and font optimization
- Data fetching patterns
- Bundle size optimization
- Routing and navigation issues
"""

from typing import Dict, Set

from core import BaseAnalyzer, Pattern, Category, Severity


class NextJSAnalyzer(BaseAnalyzer):
    """
    Analyzer for Next.js-specific anti-patterns and optimizations.

    Detects issues specific to Next.js framework that can impact
    performance, SEO, and user experience.
    """

    def __init__(self):
        """Initialize the Next.js analyzer."""
        super().__init__(name="Next.js Optimization Analyzer")

    def get_file_extensions(self) -> Set[str]:
        """Get file extensions for Next.js files."""
        return {'.js', '.jsx', '.ts', '.tsx'}

    def _init_patterns(self) -> Dict[str, Pattern]:
        """Initialize Next.js-specific detection patterns."""
        return {
            # REACT SERVER COMPONENTS
            'use_client_unnecessary': Pattern(
                name='use_client_unnecessary',
                regex=r'["\']use client["\'].*export.*function.*\{[^}]*\}(?!.*useState|.*useEffect|.*onClick)',
                category=Category.BUNDLE_SIZE,
                severity=Severity.HIGH,
                description='"use client" unnecessary - can be Server Component',
                impact='Bundle size +50KB, no SSR, SEO affected',
                solution='Remove "use client" if not using hooks/events',
                metadata={
                    'app_router': True,
                    'nextjs_version': '13+'
                }
            ),

            'fetch_client_side': Pattern(
                name='fetch_client_side',
                regex=r'(useEffect|onClick).*fetch\(',
                category=Category.PERFORMANCE,
                severity=Severity.MEDIUM,
                description='Fetch in client (move to server when possible)',
                impact='Additional latency, exposes API keys',
                solution='Move to Server Component or API Route',
                metadata={}
            ),

            # IMAGE OPTIMIZATION
            'img_tag_no_next_image': Pattern(
                name='img_tag_no_next_image',
                regex=r'<img\s+src=',
                category=Category.PERFORMANCE,
                severity=Severity.HIGH,
                description='<img> instead of next/image',
                impact='No optimization: CLS, no lazy load, no WebP',
                solution='Use <Image> from next/image',
                metadata={
                    'example_good': 'import Image from "next/image";\n<Image src="/photo.jpg" width={500} height={300} alt="..." />'
                }
            ),

            'next_image_no_sizes': Pattern(
                name='next_image_no_sizes',
                regex=r'<Image[^>]*(?!.*sizes=)',
                category=Category.PERFORMANCE,
                severity=Severity.MEDIUM,
                description='Next Image without sizes prop',
                impact='Loads wrong image size for viewport',
                solution='Add sizes prop for responsive images',
                metadata={
                    'example_good': '<Image sizes="(max-width: 768px) 100vw, 50vw" ... />'
                }
            ),

            'image_no_priority': Pattern(
                name='image_no_priority',
                regex=r'<Image[^>]*src=["\'][^"\']*hero[^"\']*["\'][^>]*(?!.*priority)',
                category=Category.PERFORMANCE,
                severity=Severity.MEDIUM,
                description='Hero/above-fold image without priority',
                impact='Slower LCP (Largest Contentful Paint)',
                solution='Add priority prop to above-fold images',
                metadata={
                    'example_good': '<Image src="/hero.jpg" priority />'
                }
            ),

            # FONTS
            'font_no_optimization': Pattern(
                name='font_no_optimization',
                regex=r'@font-face|<link.*fonts\.googleapis',
                category=Category.PERFORMANCE,
                severity=Severity.MEDIUM,
                description='Fonts without optimization',
                impact='FOUT, layout shift, slow load',
                solution='Use next/font for auto-optimization',
                metadata={
                    'example_good': 'import { Inter } from "next/font/google";\nconst inter = Inter({ subsets: ["latin"] });'
                }
            ),

            # DATA FETCHING
            'getserversideprops_for_static': Pattern(
                name='getserversideprops_for_static',
                regex=r'export.*getServerSideProps.*\{[^}]*\}',
                category=Category.PERFORMANCE,
                severity=Severity.HIGH,
                description='getServerSideProps for static data',
                impact='Server rendering on every request (slow)',
                solution='Use getStaticProps for static data or App Router',
                metadata={
                    'pages_router': True
                }
            ),

            'no_revalidate': Pattern(
                name='no_revalidate',
                regex=r'getStaticProps.*\{(?!.*revalidate)',
                category=Category.PERFORMANCE,
                severity=Severity.MEDIUM,
                description='getStaticProps without revalidate (ISR)',
                impact='Stale data until rebuild',
                solution='Add revalidate for Incremental Static Regeneration',
                metadata={
                    'example_good': 'return { props: {...}, revalidate: 60 }'
                }
            ),

            'fetch_no_cache': Pattern(
                name='fetch_no_cache',
                regex=r'fetch\([^)]*\)(?!.*cache:)',
                category=Category.PERFORMANCE,
                severity=Severity.MEDIUM,
                description='fetch without cache strategy (App Router)',
                impact='No caching, repeated requests',
                solution='Specify cache strategy: force-cache, no-store, or revalidate',
                metadata={
                    'app_router': True,
                    'example_good': 'fetch(url, { cache: "force-cache", next: { revalidate: 3600 } })'
                }
            ),

            # METADATA & SEO
            'no_metadata_export': Pattern(
                name='no_metadata_export',
                regex=r'export\s+default\s+function.*Page(?!.*export.*metadata)',
                category=Category.BEST_PRACTICE,
                severity=Severity.MEDIUM,
                description='Page without metadata export',
                impact='Poor SEO, missing meta tags',
                solution='Export metadata object or generateMetadata function',
                metadata={
                    'app_router': True,
                    'example_good': 'export const metadata = { title: "...", description: "..." };'
                }
            ),

            # ROUTING & NAVIGATION
            'anchor_for_internal': Pattern(
                name='anchor_for_internal',
                regex=r'<a\s+href=["\']\/[^"\']*["\']',
                category=Category.PERFORMANCE,
                severity=Severity.HIGH,
                description='<a> tag for internal navigation',
                impact='Full page reload, lost client-side state',
                solution='Use <Link> from next/link for internal routes',
                metadata={
                    'example_good': 'import Link from "next/link";\n<Link href="/about">About</Link>'
                }
            ),

            'router_push_without_prefetch': Pattern(
                name='router_push_without_prefetch',
                regex=r'router\.push\([^)]*\)',
                category=Category.PERFORMANCE,
                severity=Severity.LOW,
                description='router.push without prefetch consideration',
                impact='Slower navigation',
                solution='Use <Link> for prefetching or router.prefetch()',
                metadata={}
            ),

            # BUNDLE SIZE
            'import_entire_library': Pattern(
                name='import_entire_library',
                regex=r'import\s+\w+\s+from\s+["\'](@mui/material|lodash|moment)["\']',
                category=Category.BUNDLE_SIZE,
                severity=Severity.HIGH,
                description='Importing entire library instead of specific modules',
                impact='Large bundle size (+100KB to +500KB)',
                solution='Import only needed components/functions',
                metadata={
                    'example_bad': 'import Button from "@mui/material"',
                    'example_good': 'import Button from "@mui/material/Button"'
                }
            ),

            'no_dynamic_import': Pattern(
                name='no_dynamic_import',
                regex=r'import\s+.*Modal|Dialog|Chart.*from',
                category=Category.BUNDLE_SIZE,
                severity=Severity.MEDIUM,
                description='Heavy component without dynamic import',
                impact='Increases initial bundle size',
                solution='Use dynamic import for modals, charts, heavy components',
                metadata={
                    'example_good': 'const Modal = dynamic(() => import("./Modal"), { ssr: false });'
                }
            ),

            # API ROUTES
            'api_route_no_method_check': Pattern(
                name='api_route_no_method_check',
                regex=r'export\s+default\s+(?:async\s+)?function.*handler[^{]*\{(?!.*req\.method)',
                category=Category.SECURITY,
                severity=Severity.MEDIUM,
                description='API route without HTTP method check',
                impact='Unintended method access',
                solution='Check req.method and return 405 for unsupported methods',
                metadata={
                    'example_good': 'if (req.method !== "POST") return res.status(405).end();'
                }
            ),

            'api_route_no_cors': Pattern(
                name='api_route_no_cors',
                regex=r'export\s+default.*handler',
                category=Category.SECURITY,
                severity=Severity.LOW,
                description='API route without CORS headers',
                impact='CORS errors in production',
                solution='Add CORS headers or use middleware',
                metadata={}
            ),

            # CONFIGURATION
            'next_config_unoptimized_images': Pattern(
                name='next_config_unoptimized_images',
                regex=r'unoptimized:\s*true',
                category=Category.PERFORMANCE,
                severity=Severity.HIGH,
                description='Image optimization disabled',
                impact='Larger images, no WebP conversion',
                solution='Remove unoptimized: true unless necessary',
                metadata={}
            ),

            'missing_compiler_options': Pattern(
                name='missing_compiler_options',
                regex=r'module\.exports\s*=\s*\{(?!.*compiler)',
                category=Category.PERFORMANCE,
                severity=Severity.LOW,
                description='Missing compiler optimizations in next.config',
                impact='Larger bundle, slower compilation',
                solution='Add compiler options: removeConsole, reactRemoveProperties',
                metadata={
                    'example_good': 'compiler: { removeConsole: { exclude: ["error", "warn"] } }'
                }
            ),

            # STREAMING & SUSPENSE
            'loading_without_suspense': Pattern(
                name='loading_without_suspense',
                regex=r'export.*Loading.*function(?!.*Suspense)',
                category=Category.PERFORMANCE,
                severity=Severity.LOW,
                description='Loading component without Suspense usage',
                impact='No streaming, slower perceived performance',
                solution='Wrap async components in Suspense boundaries',
                metadata={
                    'app_router': True
                }
            ),
        }
