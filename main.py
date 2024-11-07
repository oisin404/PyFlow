import ast
import graphviz
import sys
import os

class FlowchartGenerator(ast.NodeVisitor):
    def __init__(self):
        self.graph = graphviz.Digraph()
        self.graph.attr(rankdir='TB')
    def visit_FunctionDef(self, node):
        self.graph.node(node.name, shape='box')
        prev_node = node.name
        for stmt in node.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                label = f"Call: {stmt.value.func.id}"
            elif isinstance(stmt, ast.Assign):
                if isinstance(stmt.targets[0], ast.Name):
                    label = f"Assign: {stmt.targets[0].id}"
                elif isinstance(stmt.targets[0], ast.Attribute):
                    label = f"Assign: {stmt.targets[0].attr}"
                else:
                    label = "Assign"
            else:
                label = type(stmt).__name__
            self.graph.node(str(id(stmt)), label=label)
            self.graph.edge(prev_node, str(id(stmt)))
            self.visit(stmt)
        self.generic_visit(node)

    def visit_If(self, node):
        self.graph.node(str(id(node.test)), label=type(node.test).__name__)
        self.graph.edge(str(id(node)), str(id(node.test)))
        self.visit(node.test)
        prev_node = str(id(node))
        for stmt in node.body:
            self.graph.edge(prev_node, str(id(stmt)))
            prev_node = str(id(stmt))
            self.visit(stmt)
        if node.orelse:
            for stmt in node.orelse:
                self.graph.edge(prev_node, str(id(stmt)))
                prev_node = str(id(stmt))
                self.visit(stmt)
        self.generic_visit(node)

    def visit_While(self, node):
        self.graph.node(str(id(node)), label='while', shape='diamond')
        self.graph.edge(str(id(node)), str(id(node.test)))
        self.visit(node.test)
        prev_node = str(id(node))
        for stmt in node.body:
            self.graph.edge(prev_node, str(id(stmt)))
            prev_node = str(id(stmt))
            self.visit(stmt)
        if node.orelse:
            for stmt in node.orelse:
                self.graph.edge(prev_node, str(id(stmt)))
                prev_node = str(id(stmt))
                self.visit(stmt)
        self.generic_visit(node)
        def visit_For(self, node):
            self.graph.node(str(id(node)), label='for', shape='diamond')
            self.graph.edge(str(id(node)), str(id(node.target)), label='target')
            self.graph.node(str(id(node.target)), label=type(node.target).__name__)
            self.graph.edge(str(id(node.target)), str(id(node.iter)), label='iter')
            self.graph.node(str(id(node.iter)), label=type(node.iter).__name__)
            self.visit(node.target)
            self.visit(node.iter)
            prev_node = str(id(node))
            for stmt in node.body:
                self.graph.edge(prev_node, str(id(stmt)), label='body')
                prev_node = str(id(stmt))
                self.visit(stmt)
            if node.orelse:
                for stmt in node.orelse:
                    self.graph.edge(prev_node, str(id(stmt)), label='orelse')
                    prev_node = str(id(stmt))
                    self.visit(stmt)
            self.generic_visit(node)

    def generate(self, filename, output_filename):
        with open(filename, "r") as source:
            tree = ast.parse(source.read())
        self.visit(tree)
        self.graph.render(output_filename, format='pdf', cleanup=True)

if __name__ == "__main__":
    filename = sys.argv[1]
    generator = FlowchartGenerator()
    output_filename = os.path.join(os.getcwd(), os.path.basename(filename) + '_flowchart')
    generator.generate(filename, output_filename)
    print(f"Flowchart generated and saved as {output_filename}.pdf")