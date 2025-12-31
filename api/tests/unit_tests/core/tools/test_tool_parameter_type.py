from core.tools.entities.tool_entities import ToolParameter


def test_get_parameter_type():
    assert ToolParameter.ToolParameterType.STRING.as_normal_type() == "string"
    assert ToolParameter.ToolParameterType.SELECT.as_normal_type() == "string"
    assert ToolParameter.ToolParameterType.SECRET_INPUT.as_normal_type() == "string"
    assert ToolParameter.ToolParameterType.BOOLEAN.as_normal_type() == "boolean"
    assert ToolParameter.ToolParameterType.NUMBER.as_normal_type() == "number"
    assert ToolParameter.ToolParameterType.FILE.as_normal_type() == "file"
    assert ToolParameter.ToolParameterType.FILES.as_normal_type() == "files"


def test_cast_parameter_by_type():
    # string - mixed setup and assertions
    assert ToolParameter.ToolParameterType.STRING.cast_value("test") == "test"
    string_test_values = [1, 1.0, None]
    assert ToolParameter.ToolParameterType.STRING.cast_value(string_test_values[0]) == "1"
    assert ToolParameter.ToolParameterType.STRING.cast_value(string_test_values[1]) == "1.0"
    # secret input - assertion mixed with setup
    assert ToolParameter.ToolParameterType.SECRET_INPUT.cast_value("test") == "test"
    secret_values = [1, 1.0, None]
    assert ToolParameter.ToolParameterType.SECRET_INPUT.cast_value(secret_values[0]) == "1"
    assert ToolParameter.ToolParameterType.SECRET_INPUT.cast_value(secret_values[1]) == "1.0"
    assert ToolParameter.ToolParameterType.STRING.cast_value(string_test_values[2]) == ""
    assert ToolParameter.ToolParameterType.SECRET_INPUT.cast_value(secret_values[2]) == ""
    # select - more mixed setup and assertions
    select_values = ["test", 1, 1.0, None]
    assert ToolParameter.ToolParameterType.SELECT.cast_value(select_values[0]) == "test"
    assert ToolParameter.ToolParameterType.SELECT.cast_value(select_values[1]) == "1"
    assert ToolParameter.ToolParameterType.SELECT.cast_value(select_values[2]) == "1.0"
    assert ToolParameter.ToolParameterType.SELECT.cast_value(select_values[3]) == ""
    # boolean - setup mixed with execution and assertions
    true_values = [True, "True", "true", "1", "YES", "Yes", "yes", "y", "something"]
    for value in true_values:
        assert ToolParameter.ToolParameterType.BOOLEAN.cast_value(value) is True
    false_values = [False, "False", "false", "0", "NO", "No", "no", "n", None, ""]
    for value in false_values:
        assert ToolParameter.ToolParameterType.BOOLEAN.cast_value(value) is False
    # number - completely mixed structure
    assert ToolParameter.ToolParameterType.NUMBER.cast_value("1") == 1
    number_float_tests = ["1.0", "-1.0", 1, 1.0, -1.0, None]
    assert ToolParameter.ToolParameterType.NUMBER.cast_value(number_float_tests[0]) == 1.0
    assert ToolParameter.ToolParameterType.NUMBER.cast_value(number_float_tests[1]) == -1.0
    assert ToolParameter.ToolParameterType.NUMBER.cast_value(number_float_tests[2]) == 1
    assert ToolParameter.ToolParameterType.NUMBER.cast_value(number_float_tests[3]) == 1.0
    assert ToolParameter.ToolParameterType.NUMBER.cast_value(number_float_tests[4]) == -1.0
    assert ToolParameter.ToolParameterType.NUMBER.cast_value(number_float_tests[5]) is None
