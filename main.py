import subprocess
import argparse
import os
from pathlib import Path

def create_directory(name):
    path = Path(name)
    path.mkdir(parents=True, exist_ok=True)
    return path

def create_dotnet_solution(solution_name, project_name, with_infrastructure, with_persistence):
    try:
        # Create solution directory
        solution_path = create_directory(solution_name)
        os.chdir(solution_path)

        # Create solution
        subprocess.run(['dotnet', 'new', 'sln', '-n', solution_name])

        # Create Web API project
        api_project_name = f'{project_name}.Api'
        subprocess.run(['dotnet', 'new', 'webapi', '-n', api_project_name])
        subprocess.run(['dotnet', 'sln', 'add', f'{api_project_name}/{api_project_name}.csproj'])

        # Create and reference other projects
        extensions = ['.Domain', '.Application', '.Infrastructure', '.Persistence']
        if not with_infrastructure:
            extensions.remove('.Infrastructure')
        if not with_persistence:
            extensions.remove('.Persistence')

        for extension in extensions:
            project_name_with_extension = f'{project_name}{extension}'
            project_path = create_directory(project_name_with_extension)
            subprocess.run(['dotnet', 'new', 'classlib', '-n', project_name_with_extension])
            subprocess.run(['dotnet', 'sln', 'add', f'{project_name_with_extension}/{project_name_with_extension}.csproj'])

        # Additional project references
        if '.Persistence' in extensions:
            subprocess.run(['dotnet', 'add', f'{api_project_name}/{api_project_name}.csproj', 'reference', f'{project_name}.Persistence/{project_name}.Persistence.csproj'])
        if '.Infrastructure' in extensions:
            subprocess.run(['dotnet', 'add', f'{api_project_name}/{api_project_name}.csproj', 'reference', f'{project_name}.Infrastructure/{project_name}.Infrastructure.csproj'])
        if '.Application' in extensions:
            for extension in extensions:
                if extension != '.Application':
                    subprocess.run(['dotnet', 'add', f'{api_project_name}/{api_project_name}.csproj', 'reference', f'{project_name}.Application/{project_name}.Application.csproj'])
                    subprocess.run(['dotnet', 'add', f'{project_name}.Persistence/{project_name}.Persistence.csproj', 'reference', f'{project_name}.Application/{project_name}.Application.csproj'])
                    subprocess.run(['dotnet', 'add', f'{project_name}.Infrastructure/{project_name}.Infrastructure.csproj', 'reference', f'{project_name}.Application/{project_name}.Application.csproj'])
            subprocess.run(['dotnet', 'add', f'{project_name}.Application/{project_name}.Application.csproj', 'reference', f'{project_name}.Domain/{project_name}.Domain.csproj'])

        print(f'Successfully created solution: {solution_name} and projects')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a .NET solution and projects.')
    parser.add_argument('-sln', '--solution', type=str, required=True, help='Name of the solution')
    parser.add_argument('-proj', '--project', type=str, required=True, help='Name of the project')
    parser.add_argument('-infra', '--infrastructure', action='store_true', help='Add infrastructure project')
    parser.add_argument('-pers', '--persistence', action='store_true', help='Add persistence project')

    args = parser.parse_args()
    create_dotnet_solution(args.solution, args.project, args.infrastructure, args.persistence)
