from flask import Flask, render_template, request, jsonify, session
import re
import io
import time
from collections import Counter
import os
import PyPDF2
import docx
import json

app = Flask(__name__)
app.secret_key = 'cv_analyzer_secret_key_2024'

JOB_DESCRIPTION_FILES = {
    'data_scientist': ('Data Scientist', 'job_desc_data_scientist.txt'),
    'software_tester': ('Software Tester', 'job_desc_software_tester.txt'),
    'web_developer': ('Web Developer', 'job_desc_web_developer.txt')
}

# Common skills list
COMMON_SKILLS = [
    'python', 'java', 'c++', 'c#', 'javascript', 'sql', 'excel', 'powerpoint', 'word',
    'machine learning', 'deep learning', 'nlp', 'data analysis', 'data visualization',
    'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'aws', 'azure', 'docker', 'kubernetes',
    'project management', 'leadership', 'communication', 'sales', 'marketing', 'seo', 'git', 'linux',
    'html', 'css', 'react', 'angular', 'vue', 'node.js', 'mongodb', 'postgresql', 'mysql'
]

ALGORITHMS = ['brute_force', 'rabin_karp', 'kmp']
CV_SIZE_THRESHOLD = 5000  

# STRING MATCHING ALGORITHMS 

def brute_force_search(text, pattern, case_sensitive=False):
    """Brute Force string matching algorithm."""
    if not case_sensitive:
        text = text.lower()
        pattern = pattern.lower()
    
    n = len(text)
    m = len(pattern)
    matches=[]
    comparisons = 0
    
    start_time = time.perf_counter()
    
    for i in range(n - m + 1):
        j = 0
        while j < m and text[i + j] == pattern[j]:
            comparisons += 1
            j += 1
        comparisons += 1  #failed comparison
        
        if j == m:
            matches.append(i)
    
    end_time = time.perf_counter()
    execution_time = (end_time - start_time) * 1000  #conv to milliseconds
    
    return {
        'matches': matches,
        'count': len(matches),
        'comparisons': comparisons,
        'execution_time': execution_time
    }


def rabin_karp_search(text, pattern, case_sensitive=False, base=256, prime=101):
    """Rabin-Karp string matching algorithm."""
    if not case_sensitive:
        text = text.lower()
        pattern = pattern.lower()
    
    n = len(text)
    m = len(pattern)
    matches = []
    comparisons = 0
    
    if n < m:
        return {'matches': [], 'count': 0, 'comparisons': 0, 'execution_time': 0}
    
    start_time = time.perf_counter()
    
    #calculating  hash of pattern and first window of text
    pattern_hash = 0
    text_hash = 0
    h = 1
    
    # The value of h would be "pow(base, m-1) % prime"
    for i in range(m - 1):
        h = (h * base) % prime
    
    #calculating initial hash values
    for i in range(m):
        pattern_hash = (base * pattern_hash + ord(pattern[i])) % prime
        text_hash = (base * text_hash + ord(text[i])) % prime
    
    #sliding the pattern over text one by one
    for i in range(n - m + 1):
        #checking hash values of current window
        if pattern_hash == text_hash:
            #checking characters one by one if hashes match
            j = 0
            while j < m:
                comparisons += 1
                if text[i + j] != pattern[j]:
                    break
                j += 1
            
            if j == m:
                matches.append(i)

        #calculating hash for next window of text
        if i < n - m:
            text_hash = (base * (text_hash - ord(text[i]) * h) + ord(text[i + m])) % prime
            #handling negative hash values
            if text_hash < 0:
                text_hash = text_hash + prime
    
    end_time = time.perf_counter()
    execution_time = (end_time - start_time) * 1000
    
    return {
        'matches': matches,
        'count': len(matches),
        'comparisons': comparisons,
        'execution_time': execution_time
    }


def kmp_search(text, pattern, case_sensitive=False):
    """Knuth-Morris-Pratt string matching algorithm."""
    if not case_sensitive:
        text = text.lower()
        pattern = pattern.lower()
    
    n = len(text)
    m = len(pattern)
    matches = []
    comparisons = 0
    
    if m == 0:
        return {'matches': [], 'count': 0, 'comparisons': 0, 'execution_time': 0}
    
    start_time = time.perf_counter()
    
    #preprocess pattern: compute longest prefix suffix (LPS) array
    lps = [0] * m
    length = 0  #length of previous longest prefix suffix
    i = 1
    
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    
    #searching pattern in text
    i = 0  # index for text
    j = 0  # index for pattern
    
    while i < n:
        comparisons += 1
        if pattern[j] == text[i]:
            i += 1
            j += 1
        
        if j == m:
            matches.append(i - j)
            j = lps[j - 1]
        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    
    end_time = time.perf_counter()
    execution_time = (end_time - start_time) * 1000
    
    return {
        'matches': matches,
        'count': len(matches),
        'comparisons': comparisons,
        'execution_time': execution_time
    }


#TEXT EXTRACTION 

def extract_text_from_pdf(file_bytes):
    """Extract text from PDF file."""
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = []
    for page in reader.pages:
        try:
            text.append(page.extract_text() or '')
        except Exception:
            text.append('')
    return '\n'.join(text)


def extract_text_from_docx(file_bytes):
    """Extract text from DOCX file."""
    doc = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs]
    return '\n'.join(paragraphs)


def extract_text(uploaded_file):
    """Extract text from uploaded file."""
    try:
        #resetting file pointer to beginning
        uploaded_file.seek(0)
        file_bytes = uploaded_file.read()
        
        #getting content type
        content_type = uploaded_file.content_type
        
        # If content type not set, try to detect from filename
        if not content_type or content_type == 'application/octet-stream':
            filename = uploaded_file.filename.lower()
            if filename.endswith('.pdf'):
                content_type = 'application/pdf'
            elif filename.endswith('.docx'):
                content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif filename.endswith('.doc'):
                content_type = 'application/msword'
        
        if content_type == 'application/pdf':
            return extract_text_from_pdf(file_bytes)
        elif content_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']:
            return extract_text_from_docx(file_bytes)
        else:
            # Trying PDF as fallback
            try:
                return extract_text_from_pdf(file_bytes)
            except:
                return ''
    except Exception as e:
        return ''


#CV ANALYSIS FUNCTIONS 

def find_keywords_in_text(text, keywords, algorithm='brute_force', case_sensitive=False):
    """Find all keywords in text using specified algorithm."""
    results = {}
    algorithm_func = {
        'brute_force': brute_force_search,
        'rabin_karp': rabin_karp_search,
        'kmp': kmp_search
    }
    
    func = algorithm_func.get(algorithm, brute_force_search)
    
    for keyword in keywords:
        result = func(text, keyword, case_sensitive)
        results[keyword] = result
    
    return results


def calculate_relevance_score(matched_keywords, total_keywords):
    """Calculate relevance score as percentage."""
    if total_keywords == 0:
        return 0.0
    return (len(matched_keywords) / total_keywords) * 100


def create_scenario_template():
    """Create a fresh metrics template for scenario tracking."""
    return {
        algo: {
            'total_time': 0.0,
            'total_comparisons': 0,
            'sample_count': 0,
            'keyword_instances': 0
        }
        for algo in ALGORITHMS
    }


def finalize_scenario_metrics(tracker):
    """Convert raw scenario tracker data into summary statistics."""
    summary = {}
    for algo, stats in tracker.items():
        sample_count = stats['sample_count']
        keyword_instances = stats['keyword_instances']

        summary[algo] = {
            'total_time': round(stats['total_time'], 4),
            'avg_time_per_cv': round(stats['total_time'] / sample_count, 4) if sample_count else 0,
            'avg_time_per_keyword': round(stats['total_time'] / keyword_instances, 4) if keyword_instances else 0,
            'total_comparisons': stats['total_comparisons'],
            'avg_comparisons_per_cv': round(stats['total_comparisons'] / sample_count, 2) if sample_count else 0,
            'avg_comparisons_per_keyword': round(stats['total_comparisons'] / keyword_instances, 2) if keyword_instances else 0,
            'sample_count': sample_count,
            'keyword_instances': keyword_instances
        }

    return summary


#FLASK ROUTES

@app.route('/')
def index():
    """Render the main CV analysis page."""
    return render_template('index.html')


@app.route('/results')
def results():
    """Render the performance comparison page."""
    return render_template('results.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_cv():
    """API endpoint for CV analysis."""
    try:
        #getting uploaded files (support multiple files)
        if 'cv_file' not in request.files:
            return jsonify({'error': 'No CV file uploaded'}), 400
        
        #getting all uploaded files (support both `cv_file` and `cv_file[]` naming)
        cv_files = []
        cv_files.extend(request.files.getlist('cv_file'))
        cv_files.extend(request.files.getlist('cv_file[]'))
        #deduplicate by filename while preserving order
        seen = set()
        unique_files = []
        for f in cv_files:
            name = getattr(f, 'filename', '')
            if not name:
                continue
            if name in seen:
                continue
            seen.add(name)
            unique_files.append(f)
        cv_files = unique_files
        if not cv_files:
            return jsonify({'error': 'No file selected'}), 400
        
        #filtering out empty files
        cv_files = [f for f in cv_files if f.filename != '']
        if not cv_files:
            return jsonify({'error': 'No valid files selected'}), 400
        
        #getting job description keywords
        job_description = request.form.get('job_description', '')
        keywords_input = request.form.get('keywords', '')
        
        #parsing keywords
        if keywords_input:
            keywords = [k.strip().lower() for k in keywords_input.split(',') if k.strip()]
        else:
            #extracting keywords from job description if provided
            if job_description:
                # Simple keyword extraction from job description
                words = re.findall(r'\b[a-zA-Z+#\-]+\b', job_description.lower())
                keywords = [w for w in words if len(w) > 3 and w not in ['with', 'this', 'that', 'from', 'have', 'will', 'work', 'the']]
                keywords = list(set(keywords))[:30]  # Limit to 30 keywords
            else:
                #using common skills as default
                keywords = COMMON_SKILLS.copy()
        
        if not keywords:
            return jsonify({'error': 'No keywords provided'}), 400
        
        #getting case sensitivity setting
        case_sensitive = request.form.get('case_sensitive', 'false') == 'true'
        
        #Algorithms to use
        algorithms = ALGORITHMS
        total_keywords = len(keywords)
        first_keyword = keywords[0] if total_keywords > 0 else None

        #processing all CV files
        cv_results = []
        overall_performance = {algo: {'total_time': 0, 'total_comparisons': 0} for algo in algorithms}
        failed_files = []

        scenario_trackers = {
            'cv_size': {
                'small': create_scenario_template(),
                'large': create_scenario_template()
            },
            'keyword_mode': {
                'single': create_scenario_template(),
                'multiple': create_scenario_template()
            }
        }
        
        for cv_file in cv_files:
            try:
                #resetting file pointer in case it was read before
                cv_file.seek(0)
                
                #extracting text from CV
                cv_text = extract_text(cv_file)
                if not cv_text.strip():
                    failed_files.append({'filename': cv_file.filename, 'error': 'No text extracted'})
                    continue  #skipping files with no text
                
                filename = cv_file.filename

                #analyzing with all three algorithms
                all_results = {}
                for algo in algorithms:
                    results = find_keywords_in_text(cv_text, keywords, algo, case_sensitive)
                    all_results[algo] = results
                
                #calculating matched/missing keywords per algorithm
                per_algo_matched = {}
                per_algo_missing = {}
                per_algo_relevance = {}
                for algo in algorithms:
                    matched = [kw for kw, res in all_results[algo].items() if res.get('count', 0) > 0]
                    missing = [kw for kw in keywords if kw not in matched]
                    per_algo_matched[algo] = matched
                    per_algo_missing[algo] = missing
                    per_algo_relevance[algo] = round(calculate_relevance_score(matched, total_keywords), 2)
                
                #calculating performance metrics for this CV
                cv_performance = {}
                for algo in algorithms:
                    total_time = sum(result['execution_time'] for result in all_results[algo].values())
                    total_comparisons = sum(result['comparisons'] for result in all_results[algo].values())
                    avg_time = total_time / total_keywords if total_keywords else 0
                    avg_comparisons = total_comparisons / total_keywords if total_keywords else 0
                    
                    cv_performance[algo] = {
                        'total_time': round(total_time, 4),
                        'avg_time': round(avg_time, 4),
                        'total_comparisons': total_comparisons,
                        'avg_comparisons': round(avg_comparisons, 2)
                    }
                    
                    #adding to overall performance
                    overall_performance[algo]['total_time'] += total_time
                    overall_performance[algo]['total_comparisons'] += total_comparisons

                size_key = 'small' if len(cv_text) <= CV_SIZE_THRESHOLD else 'large'

                for algo in algorithms:
                    # Scenario: CV size buckets
                    size_tracker = scenario_trackers['cv_size'][size_key][algo]
                    size_tracker['total_time'] += cv_performance[algo]['total_time']
                    size_tracker['total_comparisons'] += cv_performance[algo]['total_comparisons']
                    size_tracker['sample_count'] += 1
                    size_tracker['keyword_instances'] += total_keywords

                    # Scenario: multiple keyword search
                    multi_tracker = scenario_trackers['keyword_mode']['multiple'][algo]
                    multi_tracker['total_time'] += cv_performance[algo]['total_time']
                    multi_tracker['total_comparisons'] += cv_performance[algo]['total_comparisons']
                    multi_tracker['sample_count'] += 1
                    multi_tracker['keyword_instances'] += total_keywords

                    # Scenario: single keyword search (use first keyword metrics)
                    if first_keyword:
                        single_result = all_results[algo].get(first_keyword)
                        if single_result:
                            single_tracker = scenario_trackers['keyword_mode']['single'][algo]
                            single_tracker['total_time'] += single_result['execution_time']
                            single_tracker['total_comparisons'] += single_result['comparisons']
                            single_tracker['sample_count'] += 1
                            single_tracker['keyword_instances'] += 1
                
                #storing this CV's results (store brute_force summary for candidate ranking,
                #but keep per-algorithm maps for the performance page)
                cv_results.append({
                    'filename': filename,
                    'cv_text_length': len(cv_text),
                    'matched_keywords': per_algo_matched.get('brute_force', []),
                    'missing_keywords': per_algo_missing.get('brute_force', []),
                    'relevance_score': per_algo_relevance.get('brute_force', 0.0),
                    'matched_count': len(per_algo_matched.get('brute_force', [])),
                    'missing_count': len(per_algo_missing.get('brute_force', [])),
                    'performance_metrics': cv_performance,
                    # include per-algo maps for potential debugging/extended UI (not large)
                    'per_algo_matched': per_algo_matched,
                    'per_algo_missing': per_algo_missing,
                    'per_algo_relevance': per_algo_relevance
                })
            except Exception as e:
                failed_files.append({'filename': cv_file.filename, 'error': str(e)})
                continue
        
        if not cv_results:
            return jsonify({'error': f'No valid CVs could be processed. {len(failed_files)} file(s) failed.'}), 400
        
        #sorting CVs by relevance score (highest first)
        cv_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        #calculating overall performance metrics
        overall_performance_metrics = {}
        for algo in algorithms:
            total_time = overall_performance[algo]['total_time']
            total_comparisons = overall_performance[algo]['total_comparisons']
            num_cvs = len(cv_results)

            overall_performance_metrics[algo] = {
                'total_time': round(total_time, 4),
                'avg_time': round(total_time / num_cvs if num_cvs > 0 else 0, 4),
                'total_comparisons': total_comparisons,
                'avg_comparisons': round(total_comparisons / (num_cvs * total_keywords) if num_cvs > 0 and total_keywords > 0 else 0, 2)
            }

        scenario_metrics_output = {}
        for dimension, groups in scenario_trackers.items():
            scenario_metrics_output[dimension] = {}
            for group_name, tracker in groups.items():
                scenario_metrics_output[dimension][group_name] = finalize_scenario_metrics(tracker)
        
        #For compatibility with results page, also store first CV's data in a compact form
        first_cv = cv_results[0] if cv_results else None

        # Prepare compact per-algorithm maps for session (small arrays, safe to store)
        matched_map = {}
        missing_map = {}
        relevance_map = {}
        if first_cv:
            # prefer per-algo maps computed earlier if present
            matched_map = first_cv.get('per_algo_matched', {'brute_force': first_cv.get('matched_keywords', [])})
            missing_map = first_cv.get('per_algo_missing', {'brute_force': first_cv.get('missing_keywords', [])})
            relevance_map = first_cv.get('per_algo_relevance', {
                'brute_force': first_cv.get('relevance_score', 0),
                'rabin_karp': first_cv.get('relevance_score', 0),
                'kmp': first_cv.get('relevance_score', 0)
            })

        #storing results in session for results page (store summary to avoid session size limits)
        session_data = {
            'keywords': keywords,
            'total_keywords': total_keywords,
            'performance_metrics': overall_performance_metrics,
            'num_cvs': len(cv_results),
            'scenario_metrics': scenario_metrics_output,
            'cv_size_threshold': CV_SIZE_THRESHOLD,
            #storing first CV data for compatibility with results page
            'cv_text_length': first_cv['cv_text_length'] if first_cv else 0,
            # include compact per-algorithm keyword maps and relevance scores (small)
            'matched_keywords': matched_map,
            'missing_keywords': missing_map,
            'relevance_scores': relevance_map
        }
        
        #storing only if it's not too large (Flask session has ~4KB limit)
        import json
        session_json = json.dumps(session_data)
        if len(session_json) < 3500:  # Leave some margin
            session['analysis_results'] = session_data
        else:
            # If too large, store a minimal summary but still include compact keyword/relevance maps
            session['analysis_results'] = {
                'keywords': keywords,
                'total_keywords': total_keywords,
                'performance_metrics': overall_performance_metrics,
                'num_cvs': len(cv_results),
                'scenario_metrics': scenario_metrics_output,
                'cv_size_threshold': CV_SIZE_THRESHOLD,
                'cv_text_length': first_cv['cv_text_length'] if first_cv else 0,
                'matched_keywords': matched_map,
                'missing_keywords': missing_map,
                'relevance_scores': relevance_map
            }
        
        response_data = {
            'success': True,
            'keywords': keywords,
            'total_keywords': total_keywords,
            'cv_results': cv_results,
            'performance_metrics': overall_performance_metrics,
            'num_cvs': len(cv_results),
            'scenario_metrics': scenario_metrics_output,
            'cv_size_threshold': CV_SIZE_THRESHOLD,
            'failed_count': len(failed_files)
        }
        
        if failed_files:
            response_data['failed_files'] = failed_files[:10]  # Limit to first 10 failed files
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/job_description/<job_key>', methods=['GET'])
def get_job_description(job_key):
    """Provide predefined job description text for the requested template."""
    job_key = job_key.lower()
    if job_key not in JOB_DESCRIPTION_FILES:
        return jsonify({'error': 'Unknown job description template'}), 404

    title, filename = JOB_DESCRIPTION_FILES[job_key]
    file_path = os.path.join(app.root_path, filename)

    if not os.path.exists(file_path):
        return jsonify({'error': 'Template file not found'}), 404

    try:
        with open(file_path, 'r', encoding='utf-8') as template_file:
            content = template_file.read()
    except OSError as exc:
        return jsonify({'error': f'Unable to read template: {exc}'}), 500

    return jsonify({'title': title, 'content': content})


@app.route('/api/get_results', methods=['GET'])
def get_results():
    """Get stored analysis results."""
    if 'analysis_results' in session:
        return jsonify(session['analysis_results'])
    return jsonify({'error': 'No analysis results found'}), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)

