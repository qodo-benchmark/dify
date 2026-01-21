from unittest.mock import MagicMock, patch

import pytest
from core.workflow.graph_engine.entities.graph import Graph
from core.workflow.graph_engine.entities.graph_init_params import GraphInitParams
from core.workflow.graph_engine.entities.graph_runtime_state import GraphRuntimeState

from core.workflow.enums import ErrorStrategy, NodeType, WorkflowNodeExecutionStatus
from core.workflow.nodes.template_transform.template_renderer import TemplateRenderError
from core.workflow.nodes.template_transform.template_transform_node import TemplateTransformNode
from models.workflow import WorkflowType


class TestTemplateTransformNode:
    """Comprehensive test suite for TemplateTransformNode."""

    @pytest.fixture
    def mock_graph_runtime_state(self):
        """Create a mock GraphRuntimeState with variable pool."""
        mock_state = MagicMock(spec=GraphRuntimeState)
        mock_variable_pool = MagicMock()
        mock_state.variable_pool = mock_variable_pool
        return mock_state

    @pytest.fixture
    def mock_graph(self):
        """Create a mock Graph."""
        return MagicMock(spec=Graph)

    @pytest.fixture
    def graph_init_params(self):
        """Create a mock GraphInitParams."""
        return GraphInitParams(
            tenant_id="test_tenant",
            app_id="test_app",
            workflow_type=WorkflowType.WORKFLOW,
            workflow_id="test_workflow",
            graph_config={},
            user_id="test_user",
            user_from="test",
            invoke_from="test",
            call_depth=0,
        )

    @pytest.fixture
    def basic_node_data(self):
        """Create basic node data for testing."""
        return {
            "title": "Template Transform",
            "desc": "Transform data using template",
            "variables": [
                {"variable": "name", "value_selector": ["sys", "user_name"]},
                {"variable": "age", "value_selector": ["sys", "user_age"]},
            ],
            "template": "Hello {{ name }}, you are {{ age }} years old!",
        }

    def test_node_initialization(self, basic_node_data, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test that TemplateTransformNode initializes correctly."""
        node = TemplateTransformNode(
            id="test_node",
            config=basic_node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        assert node.node_type == NodeType.TEMPLATE_TRANSFORM
        assert node._node_data.title == "Template Transform"
        assert len(node._node_data.variables) == 2
        assert node._node_data.template == "Hello {{ name }}, you are {{ age }} years old!"

    def test_get_title(self, basic_node_data, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _get_title method."""
        node = TemplateTransformNode(
            id="test_node",
            config=basic_node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        assert node._get_title() == "Template Transform"

    def test_get_description(self, basic_node_data, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _get_description method."""
        node = TemplateTransformNode(
            id="test_node",
            config=basic_node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        assert node._get_description() == "Transform data using template"

    def test_get_error_strategy(self, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _get_error_strategy method."""
        node_data = {
            "title": "Test",
            "variables": [],
            "template": "test",
            "error_strategy": "fail-branch",
        }

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        assert node._get_error_strategy() == ErrorStrategy.FAIL_BRANCH

    def test_get_default_config(self):
        """Test get_default_config class method."""
        config = TemplateTransformNode.get_default_config()

        assert config["type"] == "template-transform"
        assert "config" in config
        assert "variables" in config["config"]
        assert "template" in config["config"]
        assert config["config"]["template"] == "{{ arg1 }}"

    def test_version(self):
        """Test version class method."""
        assert TemplateTransformNode.version() == "1"

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_simple_template(
        self, mock_execute, basic_node_data, mock_graph, mock_graph_runtime_state, graph_init_params
    ):
        """Test _run with simple template transformation."""
        # Setup mock variable pool
        mock_name_value = MagicMock()
        mock_name_value.to_object.return_value = "Alice"
        mock_age_value = MagicMock()
        mock_age_value.to_object.return_value = 30

        variable_map = {
            ("sys", "user_name"): mock_name_value,
            ("sys", "user_age"): mock_age_value,
        }
        mock_graph_runtime_state.variable_pool.get.side_effect = lambda selector: variable_map.get(tuple(selector))

        # Setup mock executor
        mock_execute.return_value = "Hello Alice, you are 30 years old!"

        node = TemplateTransformNode(
            id="test_node",
            config=basic_node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "Hello Alice, you are 30 years old!"
        assert result.inputs["name"] == "Alice"
        assert result.inputs["age"] == 30

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_none_values(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with None variable values."""
        node_data = {
            "title": "Test",
            "variables": [{"variable": "value", "value_selector": ["sys", "missing"]}],
            "template": "Value: {{ value }}",
        }

        mock_graph_runtime_state.variable_pool.get.return_value = None
        mock_execute.return_value = "Value: "

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.inputs["value"] is None

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_code_execution_error(
        self, mock_execute, basic_node_data, mock_graph, mock_graph_runtime_state, graph_init_params
    ):
        """Test _run when code execution fails."""
        mock_graph_runtime_state.variable_pool.get.return_value = MagicMock()
        mock_execute.side_effect = TemplateRenderError("Template syntax error")

        node = TemplateTransformNode(
            id="test_node",
            config=basic_node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.FAILED
        assert "Template syntax error" in result.error

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    @patch("core.workflow.nodes.template_transform.template_transform_node.MAX_TEMPLATE_TRANSFORM_OUTPUT_LENGTH", 10)
    def test_run_output_length_exceeds_limit(
        self, mock_execute, basic_node_data, mock_graph, mock_graph_runtime_state, graph_init_params
    ):
        """Test _run when output exceeds maximum length."""
        mock_graph_runtime_state.variable_pool.get.return_value = MagicMock()
        mock_execute.return_value = "This is a very long output that exceeds the limit"

        node = TemplateTransformNode(
            id="test_node",
            config=basic_node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.FAILED
        assert "Output length exceeds" in result.error

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_complex_jinja2_template(
        self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params
    ):
        """Test _run with complex Jinja2 template including loops and conditions."""
        node_data = {
            "title": "Complex Template",
            "variables": [
                {"variable": "items", "value_selector": ["sys", "items"]},
                {"variable": "show_total", "value_selector": ["sys", "show_total"]},
            ],
            "template": (
                "{% for item in items %}{{ item }}{% if not loop.last %}, {% endif %}{% endfor %}"
                "{% if show_total %} (Total: {{ items|length }}){% endif %}"
            ),
        }

        mock_items = MagicMock()
        mock_items.to_object.return_value = ["apple", "banana", "orange"]
        mock_show_total = MagicMock()
        mock_show_total.to_object.return_value = True

        variable_map = {
            ("sys", "items"): mock_items,
            ("sys", "show_total"): mock_show_total,
        }
        mock_graph_runtime_state.variable_pool.get.side_effect = lambda selector: variable_map.get(tuple(selector))
        mock_execute.return_value = "apple, banana, orange (Total: 3)"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "apple, banana, orange (Total: 3)"

    def test_extract_variable_selector_to_variable_mapping(self):
        """Test _extract_variable_selector_to_variable_mapping class method."""
        node_data = {
            "title": "Test",
            "variables": [
                {"variable": "var1", "value_selector": ["sys", "input1"]},
                {"variable": "var2", "value_selector": ["sys", "input2"]},
            ],
            "template": "{{ var1 }} {{ var2 }}",
        }

        mapping = TemplateTransformNode._extract_variable_selector_to_variable_mapping(
            graph_config={}, node_id="node_123", node_data=node_data
        )

        assert "node_123.var1" in mapping
        assert "node_123.var2" in mapping
        assert mapping["node_123.var1"] == ["sys", "input1"]
        assert mapping["node_123.var2"] == ["sys", "input2"]

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_empty_variables(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with no variables (static template)."""
        node_data = {
            "title": "Static Template",
            "variables": [],
            "template": "This is a static message.",
        }

        mock_execute.return_value = "This is a static message."

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "This is a static message."
        assert result.inputs == {}

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_numeric_values(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with numeric variable values."""
        node_data = {
            "title": "Numeric Template",
            "variables": [
                {"variable": "price", "value_selector": ["sys", "price"]},
                {"variable": "quantity", "value_selector": ["sys", "quantity"]},
            ],
            "template": "Total: ${{ price * quantity }}",
        }

        mock_price = MagicMock()
        mock_price.to_object.return_value = 10.5
        mock_quantity = MagicMock()
        mock_quantity.to_object.return_value = 3

        variable_map = {
            ("sys", "price"): mock_price,
            ("sys", "quantity"): mock_quantity,
        }
        mock_graph_runtime_state.variable_pool.get.side_effect = lambda selector: variable_map.get(tuple(selector))
        mock_execute.return_value = "Total: $31.5"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "Total: $31.5"

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_dict_values(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with dictionary variable values."""
        node_data = {
            "title": "Dict Template",
            "variables": [{"variable": "user", "value_selector": ["sys", "user_data"]}],
            "template": "Name: {{ user.name }}, Email: {{ user.email }}",
        }

        mock_user = MagicMock()
        mock_user.to_object.return_value = {"name": "John Doe", "email": "john@example.com"}

        mock_graph_runtime_state.variable_pool.get.return_value = mock_user
        mock_execute.return_value = "Name: John Doe, Email: john@example.com"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert "John Doe" in result.outputs["output"]
        assert "john@example.com" in result.outputs["output"]

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_list_values(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with list variable values."""
        node_data = {
            "title": "List Template",
            "variables": [{"variable": "tags", "value_selector": ["sys", "tags"]}],
            "template": "Tags: {% for tag in tags %}#{{ tag }} {% endfor %}",
        }

        mock_tags = MagicMock()
        mock_tags.to_object.return_value = ["python", "ai", "workflow"]

        mock_graph_runtime_state.variable_pool.get.return_value = mock_tags
        mock_execute.return_value = "Tags: #python #ai #workflow "

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert "#python" in result.outputs["output"]
        assert "#ai" in result.outputs["output"]
        assert "#workflow" in result.outputs["output"]

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_boolean_values(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with boolean variable values."""
        node_data = {
            "title": "Boolean Template",
            "variables": [{"variable": "is_active", "value_selector": ["sys", "active_status"]}],
            "template": "{% if is_active %}Active{% else %}Inactive{% endif %}",
        }

        mock_status = MagicMock()
        mock_status.to_object.return_value = True

        mock_graph_runtime_state.variable_pool.get.return_value = mock_status
        mock_execute.return_value = "Active"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "Active"

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_nested_dict_values(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with nested dictionary variable values."""
        node_data = {
            "title": "Nested Dict Template",
            "variables": [{"variable": "data", "value_selector": ["sys", "nested_data"]}],
            "template": "User: {{ data.user.name }}, Company: {{ data.company.name }}",
        }

        mock_data = MagicMock()
        mock_data.to_object.return_value = {
            "user": {"name": "Alice", "id": 123},
            "company": {"name": "TechCorp", "id": 456},
        }

        mock_graph_runtime_state.variable_pool.get.return_value = mock_data
        mock_execute.return_value = "User: Alice, Company: TechCorp"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert "Alice" in result.outputs["output"]
        assert "TechCorp" in result.outputs["output"]

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_filter_upper(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with upper filter."""
        node_data = {
            "title": "Filter Template",
            "variables": [{"variable": "text", "value_selector": ["sys", "input_text"]}],
            "template": "{{ text | upper }}",
        }

        mock_text = MagicMock()
        mock_text.to_object.return_value = "hello world"

        mock_graph_runtime_state.variable_pool.get.return_value = mock_text
        mock_execute.return_value = "HELLO WORLD"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "HELLO WORLD"

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_filter_lower(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with lower filter."""
        node_data = {
            "title": "Filter Template",
            "variables": [{"variable": "text", "value_selector": ["sys", "input_text"]}],
            "template": "{{ text | lower }}",
        }

        mock_text = MagicMock()
        mock_text.to_object.return_value = "HELLO WORLD"

        mock_graph_runtime_state.variable_pool.get.return_value = mock_text
        mock_execute.return_value = "hello world"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "hello world"

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_filter_length(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with length filter."""
        node_data = {
            "title": "Length Filter Template",
            "variables": [{"variable": "items", "value_selector": ["sys", "list_items"]}],
            "template": "Count: {{ items | length }}",
        }

        mock_items = MagicMock()
        mock_items.to_object.return_value = ["a", "b", "c", "d"]

        mock_graph_runtime_state.variable_pool.get.return_value = mock_items
        mock_execute.return_value = "Count: 4"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "Count: 4"

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_filter_default(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with default filter."""
        node_data = {
            "title": "Default Filter Template",
            "variables": [{"variable": "value", "value_selector": ["sys", "optional_value"]}],
            "template": "{{ value | default('N/A') }}",
        }

        mock_graph_runtime_state.variable_pool.get.return_value = None
        mock_execute.return_value = "N/A"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "N/A"

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_multiline_template(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with multiline template."""
        node_data = {
            "title": "Multiline Template",
            "variables": [
                {"variable": "name", "value_selector": ["sys", "user_name"]},
                {"variable": "email", "value_selector": ["sys", "user_email"]},
            ],
            "template": """Hello {{ name }},
Welcome to our service!
Your email: {{ email }}""",
        }

        mock_name = MagicMock()
        mock_name.to_object.return_value = "Bob"
        mock_email = MagicMock()
        mock_email.to_object.return_value = "bob@example.com"

        variable_map = {
            ("sys", "user_name"): mock_name,
            ("sys", "user_email"): mock_email,
        }
        mock_graph_runtime_state.variable_pool.get.side_effect = lambda selector: variable_map.get(tuple(selector))
        mock_execute.return_value = """Hello Bob,
Welcome to our service!
Your email: bob@example.com"""

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert "Bob" in result.outputs["output"]
        assert "bob@example.com" in result.outputs["output"]

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_string_concatenation(
        self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params
    ):
        """Test _run with string concatenation."""
        node_data = {
            "title": "Concatenation Template",
            "variables": [
                {"variable": "first", "value_selector": ["sys", "first_name"]},
                {"variable": "last", "value_selector": ["sys", "last_name"]},
            ],
            "template": "{{ first ~ ' ' ~ last }}",
        }

        mock_first = MagicMock()
        mock_first.to_object.return_value = "Jane"
        mock_last = MagicMock()
        mock_last.to_object.return_value = "Doe"

        variable_map = {
            ("sys", "first_name"): mock_first,
            ("sys", "last_name"): mock_last,
        }
        mock_graph_runtime_state.variable_pool.get.side_effect = lambda selector: variable_map.get(tuple(selector))
        mock_execute.return_value = "Jane Doe"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "Jane Doe"

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_conditional_if_else(
        self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params
    ):
        """Test _run with conditional if-else statements."""
        node_data = {
            "title": "Conditional Template",
            "variables": [{"variable": "score", "value_selector": ["sys", "test_score"]}],
            "template": "{% if score >= 90 %}A{% elif score >= 80 %}B{% else %}C{% endif %}",
        }

        mock_score = MagicMock()
        mock_score.to_object.return_value = 85

        mock_graph_runtime_state.variable_pool.get.return_value = mock_score
        mock_execute.return_value = "B"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "B"

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_loop_range(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with loop using range."""
        node_data = {
            "title": "Range Loop Template",
            "variables": [{"variable": "count", "value_selector": ["sys", "num_items"]}],
            "template": "{% for i in range(count) %}{{ i }}{% if not loop.last %}, {% endif %}{% endfor %}",
        }

        mock_count = MagicMock()
        mock_count.to_object.return_value = 5

        mock_graph_runtime_state.variable_pool.get.return_value = mock_count
        mock_execute.return_value = "0, 1, 2, 3, 4"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "0, 1, 2, 3, 4"

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_loop_index(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with loop using index."""
        node_data = {
            "title": "Loop Index Template",
            "variables": [{"variable": "items", "value_selector": ["sys", "list_items"]}],
            "template": "{% for item in items %}{{ loop.index }}. {{ item }}\n{% endfor %}",
        }

        mock_items = MagicMock()
        mock_items.to_object.return_value = ["First", "Second", "Third"]

        mock_graph_runtime_state.variable_pool.get.return_value = mock_items
        mock_execute.return_value = "1. First\n2. Second\n3. Third\n"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert "1. First" in result.outputs["output"]
        assert "2. Second" in result.outputs["output"]

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_special_characters(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with special characters in variables."""
        node_data = {
            "title": "Special Chars Template",
            "variables": [{"variable": "text", "value_selector": ["sys", "input_text"]}],
            "template": "{{ text }}",
        }

        mock_text = MagicMock()
        mock_text.to_object.return_value = "Hello @#$%^&* World!"

        mock_graph_runtime_state.variable_pool.get.return_value = mock_text
        mock_execute.return_value = "Hello @#$%^&* World!"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "Hello @#$%^&* World!"

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_unicode_characters(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with unicode characters."""
        node_data = {
            "title": "Unicode Template",
            "variables": [{"variable": "text", "value_selector": ["sys", "unicode_text"]}],
            "template": "{{ text }}",
        }

        mock_text = MagicMock()
        mock_text.to_object.return_value = "Hello 世界 🌍"

        mock_graph_runtime_state.variable_pool.get.return_value = mock_text
        mock_execute.return_value = "Hello 世界 🌍"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "Hello 世界 🌍"

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_empty_string(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with empty string variable."""
        node_data = {
            "title": "Empty String Template",
            "variables": [{"variable": "text", "value_selector": ["sys", "empty_text"]}],
            "template": "Value: '{{ text }}'",
        }

        mock_text = MagicMock()
        mock_text.to_object.return_value = ""

        mock_graph_runtime_state.variable_pool.get.return_value = mock_text
        mock_execute.return_value = "Value: ''"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "Value: ''"

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_zero_value(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with zero value."""
        node_data = {
            "title": "Zero Value Template",
            "variables": [{"variable": "num", "value_selector": ["sys", "number"]}],
            "template": "Number: {{ num }}",
        }

        mock_num = MagicMock()
        mock_num.to_object.return_value = 0

        mock_graph_runtime_state.variable_pool.get.return_value = mock_num
        mock_execute.return_value = "Number: 0"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "Number: 0"

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_negative_number(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with negative number."""
        node_data = {
            "title": "Negative Number Template",
            "variables": [{"variable": "balance", "value_selector": ["sys", "account_balance"]}],
            "template": "Balance: ${{ balance }}",
        }

        mock_balance = MagicMock()
        mock_balance.to_object.return_value = -50.25

        mock_graph_runtime_state.variable_pool.get.return_value = mock_balance
        mock_execute.return_value = "Balance: $-50.25"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "Balance: $-50.25"

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_float_precision(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with float precision."""
        node_data = {
            "title": "Float Precision Template",
            "variables": [{"variable": "value", "value_selector": ["sys", "precise_value"]}],
            "template": "Value: {{ '%.2f' % value }}",
        }

        mock_value = MagicMock()
        mock_value.to_object.return_value = 3.14159265

        mock_graph_runtime_state.variable_pool.get.return_value = mock_value
        mock_execute.return_value = "Value: 3.14"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "Value: 3.14"

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_large_number(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with large number."""
        node_data = {
            "title": "Large Number Template",
            "variables": [{"variable": "population", "value_selector": ["sys", "world_population"]}],
            "template": "Population: {{ population }}",
        }

        mock_population = MagicMock()
        mock_population.to_object.return_value = 8000000000

        mock_graph_runtime_state.variable_pool.get.return_value = mock_population
        mock_execute.return_value = "Population: 8000000000"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "Population: 8000000000"

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_mixed_types_in_list(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with mixed types in list."""
        node_data = {
            "title": "Mixed Types Template",
            "variables": [{"variable": "items", "value_selector": ["sys", "mixed_items"]}],
            "template": "{% for item in items %}{{ item }}{% if not loop.last %}, {% endif %}{% endfor %}",
        }

        mock_items = MagicMock()
        mock_items.to_object.return_value = [1, "two", 3.0, True]

        mock_graph_runtime_state.variable_pool.get.return_value = mock_items
        mock_execute.return_value = "1, two, 3.0, True"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert "1, two, 3.0, True" == result.outputs["output"]

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_empty_list(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with empty list."""
        node_data = {
            "title": "Empty List Template",
            "variables": [{"variable": "items", "value_selector": ["sys", "empty_items"]}],
            "template": "{% if items %}Has items{% else %}No items{% endif %}",
        }

        mock_items = MagicMock()
        mock_items.to_object.return_value = []

        mock_graph_runtime_state.variable_pool.get.return_value = mock_items
        mock_execute.return_value = "No items"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "No items"

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_empty_dict(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with empty dictionary."""
        node_data = {
            "title": "Empty Dict Template",
            "variables": [{"variable": "data", "value_selector": ["sys", "empty_data"]}],
            "template": "{% if data %}Has data{% else %}No data{% endif %}",
        }

        mock_data = MagicMock()
        mock_data.to_object.return_value = {}

        mock_graph_runtime_state.variable_pool.get.return_value = mock_data
        mock_execute.return_value = "No data"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "No data"

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_whitespace_control(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with whitespace control."""
        node_data = {
            "title": "Whitespace Control Template",
            "variables": [{"variable": "items", "value_selector": ["sys", "list_items"]}],
            "template": "{%- for item in items -%}{{ item }}{%- endfor -%}",
        }

        mock_items = MagicMock()
        mock_items.to_object.return_value = ["a", "b", "c"]

        mock_graph_runtime_state.variable_pool.get.return_value = mock_items
        mock_execute.return_value = "abc"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert result.outputs["output"] == "abc"

    @patch(
        "core.workflow.nodes.template_transform.template_transform_node.CodeExecutorJinja2TemplateRenderer.render_template"
    )
    def test_run_with_escape_filter(self, mock_execute, mock_graph, mock_graph_runtime_state, graph_init_params):
        """Test _run with escape filter for HTML."""
        node_data = {
            "title": "Escape Filter Template",
            "variables": [{"variable": "html", "value_selector": ["sys", "html_content"]}],
            "template": "{{ html | escape }}",
        }

        mock_html = MagicMock()
        mock_html.to_object.return_value = "<script>alert('xss')</script>"

        mock_graph_runtime_state.variable_pool.get.return_value = mock_html
        mock_execute.return_value = "&lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;"

        node = TemplateTransformNode(
            id="test_node",
            config=node_data,
            graph_init_params=graph_init_params,
            graph=mock_graph,
            graph_runtime_state=mock_graph_runtime_state,
        )

        result = node._run()

        assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert "&lt;script&gt;" in result.outputs["output"]
