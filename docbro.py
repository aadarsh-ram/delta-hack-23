import argparse
import shutil
import os
import markdown
from toc import TreeGenerate

baseURL = os.environ.get('BASE_URL', 'https://aadarsh-ram.github.io/delta-hack-23/')
project_name = os.environ.get('PROJECT_NAME', 'Sample Project')
TEMPLATE = f"""
<!DOCTYPE html>
<html>
<head>
    <base href="{baseURL}">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="referrer" content="no-referrer" />
    <meta name="referrer" content="unsafe-url" />
    <meta name="referrer" content="origin" />
    <meta name="referrer" content="no-referrer-when-downgrade" />
    <meta name="referrer" content="origin-when-cross-origin" />
    <title>Page Title</title>
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">
    """ + """
    <style>
        body {
            font-family: Helvetica,Arial,sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        code, pre {
            font-family: monospace;
        }
        .container {
            margin-top: 20px;
            margin-bottom: 20px;
        }
        footer {
            background-color: #f5f5f5;
            color: black;
            text-align: center;
        }
    </style>
</head>
<body>
<div class="container">
<a href="index.html">Back to root directory</a>
{{content}}
<a href="index.html">Back to root directory</a>
</div>
<footer>
    <h4> Made with 💛 by Aadarsh A</h4>
</footer>
</body>
</html>
"""

class Docbro:
    """
    Docbro is your brotha for generating documentation from docstrings in Python
    """
    def parse_file(self, filename):
        """
        Parse a file and return a list of docstrings
        """
        docstrings = []
        with open(filename, 'r') as project_file:
            curr_docstring = {}
            docstring_md_content = []
            can_parse = False
            can_parse_md = False

            for line in project_file:
                line = line.strip()

                # Check if we are in a docstring
                if line.startswith('docbrostart'):
                    can_parse = True

                # Check if we are at the end of a docstring
                elif line.startswith('docbroend'):
                    docstrings.append(curr_docstring)
                    curr_docstring = {}
                    can_parse = False
                
                # Check if we are parsing markdown
                elif line.startswith(':markdown_start:'):
                    can_parse_md = True

                # Check if we are at the end of markdown
                elif line.startswith(':markdown_end:'):
                    can_parse_md = False
                    curr_docstring['markdown'] = "\n".join(docstring_md_content)
                    docstring_md_content = []
                
                # Markdown doesn't need to be converted
                elif can_parse_md:
                    docstring_md_content.append(line)
                
                # Parse the docstring
                elif can_parse:
                    if line: # Ignore empty lines
                        splitted = line.split(':')
                        doc_type = splitted[1]
                        doc_value = splitted[2]

                        # Parse name, description, returns
                        if doc_type in ['name', 'description', 'returns']:
                            curr_docstring[doc_type] = doc_value.strip()
                        
                        # Parse params and raises
                        elif doc_type.split()[0] == 'param':
                            param_object = {}
                            param_object['name'] = doc_type.split()[1]
                            param_object['description'] = doc_value.strip()
                            if curr_docstring.get('params', -1) != -1:
                                curr_docstring['params'].append(param_object)
                            else:
                                curr_docstring['params'] = [param_object]
                        
                        elif doc_type.split()[0] == 'raises':
                            raise_object = {}
                            raise_object['type'] = doc_type.split()[1]
                            raise_object['description'] = doc_value.strip()
                            if curr_docstring.get('raises', -1) != -1:
                                curr_docstring['raises'].append(raise_object)
                            else:
                                curr_docstring['raises'] = [raise_object]
        return docstrings
    
    def generate_markdown(self, docstrings):
        """
        Generate markdown from a list of docstrings
        """
        markdown_output = []
        start_docstring = docstrings[0]
        markdown_output.append('# {}'.format(start_docstring['name']))
        markdown_output.append('## Description')
        markdown_output.append(start_docstring['description'])

        # Add markdown if provided
        if start_docstring.get('markdown', {}) != {}:
            markdown_output.append('#### Markdown Content')
            markdown_output.append(start_docstring['markdown'])
        
        markdown_output.append('## Functions')

        for docstring in docstrings[1:]:
            markdown_output.append('### `{}`'.format(docstring['name']))
            markdown_output.append(docstring.get('description', 'No description provided'))

            # Add markdown if provided
            if docstring.get('markdown', {}) != {}:
                markdown_output.append('#### Markdown Content')
                markdown_output.append(docstring['markdown'])
            
            # Generate markdown for params
            markdown_output.append('#### Parameters')
            if docstring.get('params', {}) == {}:
                markdown_output.append('No parameters provided')
            else:
                for param in docstring['params']:
                    markdown_output.append('- `{}`: {}'.format(param['name'], param['description']))

            # Generate markdown for returns
            markdown_output.append('#### Returns')
            if docstring.get('returns', {}) == {}:
                markdown_output.append('No return value provided')
            else:
                markdown_output.append(docstring['returns'])

            # Generate markdown for raises
            markdown_output.append('#### Raises')
            if docstring.get('raises', {}) == {}:
                markdown_output.append('No exceptions provided')
            else:
                for raise_object in docstring['raises']:
                    markdown_output.append('- `{}`: {}'.format(raise_object['type'], raise_object['description']))

        return "\n".join(markdown_output)
    
    def parse_project(self, project_path):
        """
        Parse a project and return a list of docstrings
        """
        # Remove and create docs directory if it exists
        if os.path.exists('docs'):
            shutil.rmtree('docs')
        os.makedirs('docs')

        # Remove and create project directory if it exists
        if os.path.exists(f'docs/{project_name}'):
            os.remove(f'docs/{project_name}')
        os.makedirs(f'docs/{project_name}')

        for root, dirs, files in os.walk(project_path, topdown=True):
            # Ignore directories and files
            exclude_dirs = open('.ignoredirs').readlines()
            exclude_files = open('.ignorefiles').readlines()
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            files[:] = [f for f in files if f not in exclude_files]

            # Create directories
            new_root = os.path.join(f'docs/{project_name}', root[len(project_path):])
            if not os.path.exists(new_root):
                os.makedirs(new_root)

            for file in files:
                docstrings = self.parse_file(os.path.join(root, file))
                if docstrings:
                    # Generate markdown
                    markdown_content = self.generate_markdown(docstrings)
                    converted_html = markdown.markdown(markdown_content, extensions=['extra', 'smarty'], output_format='html5')
                    # Generate html
                    final_html = TEMPLATE.replace('{{content}}', converted_html)
                    file_object = open(os.path.join(new_root, file + '.html'), 'w')
                    file_object.write(final_html)
                    file_object.close()
        
        self.create_index(f'docs/', project_name)
        return 'Docbro has generated documentation for your project!'
    
    def create_index(self, output_path, project_name):
        """
        Create an index.html file for the project
        """
        project_dir = output_path+project_name

        # Generate the table of contents markdown
        tree_gen = TreeGenerate(root=output_path)
        toc_md = '\n'.join(tree_gen.generate_toc(project_dir))

        # Generate the table of contents html
        toc_html = markdown.markdown(toc_md, extensions=['extra', 'smarty'], output_format='html5')
        header = ['<h1>Documentation for {}</h1>\n'.format(project_name)]
        header.append('<h2>📁 / </h2>\n')
        toc_html = '\n'.join(header) + toc_html
        final_html = TEMPLATE.replace('{{content}}', toc_html)

        # Write the index.html file
        file_object = open(os.path.join(output_path, 'index.html'), 'w')
        file_object.write(final_html)
        file_object.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Docbro is a tool for generating documentation from docstrings in Python')
    parser.add_argument('project_path', help='Path to the project')
    args = parser.parse_args()
    docbro = Docbro()
    print (docbro.parse_project(args.project_path))