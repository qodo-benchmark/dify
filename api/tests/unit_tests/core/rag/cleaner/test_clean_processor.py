from core.rag.cleaner.clean_processor import CleanProcessor


class TestCleanProcessor:
    """Test cases for CleanProcessor.clean method."""

    def test_clean_default_removal_of_invalid_symbols(self):
        """Test default cleaning removes invalid symbols."""
        # Test <| replacement
        assert CleanProcessor.clean("text<|with<|invalid", None) == "text<with<invalid"

        # Test |> replacement
        assert CleanProcessor.clean("text|>with|>invalid", None) == "text>with>invalid"

        # Test removal of control characters
        text_with_control = "normal\x00text\x1fwith\x07control\x7fchars"
        expected = "normaltextwithcontrolchars"
        assert CleanProcessor.clean(text_with_control, None) == expected

        # Test U+FFFE removal
        text_with_ufffe = "normal\ufffepadding"
        expected = "normalpadding"
        assert CleanProcessor.clean(text_with_ufffe, None) == expected

    def test_clean_with_none_process_rule(self):
        """Test cleaning with None process_rule - only default cleaning applied."""
        text = "Hello<|World\x00"
        expected = "Hello<World"
        assert CleanProcessor.clean(text, None) == expected

    def test_clean_with_empty_process_rule(self):
        """Test cleaning with empty process_rule dict - only default cleaning applied."""
        text = "Hello<|World\x00"
        expected = "Hello<World"
        assert CleanProcessor.clean(text, {}) == expected

    def test_clean_with_empty_rules(self):
        """Test cleaning with empty rules - only default cleaning applied."""
        text = "Hello<|World\x00"
        expected = "Hello<World"
        assert CleanProcessor.clean(text, {"rules": {}}) == expected

    def test_clean_remove_extra_spaces_enabled(self):
        """Test remove_extra_spaces rule when enabled."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_extra_spaces", "enabled": True}]}}

        # Test multiple newlines reduced to two
        text = "Line1\n\n\n\n\nLine2"
        expected = "Line1\n\nLine2"
        assert CleanProcessor.clean(text, process_rule) == expected

        # Test various whitespace characters reduced to single space
        text = "word1\u2000\u2001\t\t  \u3000word2"
        expected = "word1 word2"
        assert CleanProcessor.clean(text, process_rule) == expected

        # Test combination of newlines and spaces
        text = "Line1\n\n\n\n  \t  Line2"
        expected = "Line1\n\n Line2"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_remove_extra_spaces_disabled(self):
        """Test remove_extra_spaces rule when disabled."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_extra_spaces", "enabled": False}]}}

        text = "Line1\n\n\n\n\nLine2  with  spaces"
        # Should only apply default cleaning (no invalid symbols here)
        assert CleanProcessor.clean(text, process_rule) == text

    def test_clean_remove_urls_emails_enabled(self):
        """Test remove_urls_emails rule when enabled."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        # Test email removal
        text = "Contact us at test@example.com for more info"
        expected = "Contact us at  for more info"
        assert CleanProcessor.clean(text, process_rule) == expected

        # Test URL removal
        text = "Visit https://example.com or http://test.org"
        expected = "Visit  or "
        assert CleanProcessor.clean(text, process_rule) == expected

        # Test both email and URL
        text = "Email me@test.com and visit https://site.com"
        expected = "Email  and visit "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_preserve_markdown_links_and_images(self):
        """Test that markdown links and images are preserved when removing URLs."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        # Test markdown link preservation
        text = "Check [Google](https://google.com) for info"
        expected = "Check [Google](https://google.com) for info"
        assert CleanProcessor.clean(text, process_rule) == expected

        # Test markdown image preservation
        text = "Image: ![alt](https://example.com/image.png)"
        expected = "Image: ![alt](https://example.com/image.png)"
        assert CleanProcessor.clean(text, process_rule) == expected

        # Test both link and image preservation
        text = "[Link](https://link.com) and ![Image](https://image.com/img.jpg)"
        expected = "[Link](https://link.com) and ![Image](https://image.com/img.jpg)"
        assert CleanProcessor.clean(text, process_rule) == expected

        # Test that non-markdown URLs are still removed
        text = "Check [Link](https://keep.com) but remove https://remove.com"
        expected = "Check [Link](https://keep.com) but remove "
        assert CleanProcessor.clean(text, process_rule) == expected

        # Test email removal alongside markdown preservation
        text = "Email: test@test.com, link: [Click](https://site.com)"
        expected = "Email: , link: [Click](https://site.com)"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_remove_urls_emails_disabled(self):
        """Test remove_urls_emails rule when disabled."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": False}]}}

        text = "Email test@example.com visit https://example.com"
        # Should only apply default cleaning
        assert CleanProcessor.clean(text, process_rule) == text

    def test_clean_both_rules_enabled(self):
        """Test both pre-processing rules enabled together."""
        process_rule = {
            "rules": {
                "pre_processing_rules": [
                    {"id": "remove_extra_spaces", "enabled": True},
                    {"id": "remove_urls_emails", "enabled": True},
                ]
            }
        }

        text = "Hello\n\n\n\n  World  test@example.com  \n\n\nhttps://example.com"
        expected = "Hello\n\n World  \n\n"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_with_markdown_link_and_extra_spaces(self):
        """Test markdown link preservation with extra spaces removal."""
        process_rule = {
            "rules": {
                "pre_processing_rules": [
                    {"id": "remove_extra_spaces", "enabled": True},
                    {"id": "remove_urls_emails", "enabled": True},
                ]
            }
        }

        text = "[Link](https://example.com)\n\n\n\n  Text  https://remove.com"
        expected = "[Link](https://example.com)\n\n Text "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_unknown_rule_id_ignored(self):
        """Test that unknown rule IDs are silently ignored."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "unknown_rule", "enabled": True}]}}

        text = "Hello<|World\x00"
        expected = "Hello<World"
        # Only default cleaning should be applied
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_empty_text(self):
        """Test cleaning empty text."""
        assert CleanProcessor.clean("", None) == ""
        assert CleanProcessor.clean("", {}) == ""
        assert CleanProcessor.clean("", {"rules": {}}) == ""

    def test_clean_text_with_only_invalid_symbols(self):
        """Test text containing only invalid symbols."""
        text = "<|<|\x00\x01\x02\ufffe|>|>"
        # <| becomes <, |> becomes >, control chars and U+FFFE are removed
        assert CleanProcessor.clean(text, None) == "<<>>"

    def test_clean_multiple_markdown_links_preserved(self):
        """Test multiple markdown links are all preserved."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "[One](https://one.com) [Two](http://two.org) [Three](https://three.net)"
        expected = "[One](https://one.com) [Two](http://two.org) [Three](https://three.net)"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_markdown_link_text_as_url(self):
        """Test markdown link where the link text itself is a URL."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        # Link text that looks like URL should be preserved
        text = "[https://text-url.com](https://actual-url.com)"
        expected = "[https://text-url.com](https://actual-url.com)"
        assert CleanProcessor.clean(text, process_rule) == expected

        # Text URL without markdown should be removed
        text = "https://text-url.com https://actual-url.com"
        expected = " "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_complex_markdown_link_content(self):
        """Test markdown links with complex content - known limitation with brackets in link text."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        # Note: The regex pattern [^\]]* cannot handle ] within link text
        # This is a known limitation - the pattern stops at the first ]
        text = "[Text with [brackets] and (parens)](https://example.com)"
        # Actual behavior: only matches up to first ], URL gets removed
        expected = "[Text with [brackets] and (parens)]("
        assert CleanProcessor.clean(text, process_rule) == expected

        # Test that properly formatted markdown links work
        text = "[Text with (parens) and symbols](https://example.com)"
        expected = "[Text with (parens) and symbols](https://example.com)"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_mixed_content_with_markdown_and_plain_urls(self):
        """Test content with both markdown links and plain URLs."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Visit [Google](https://google.com) or https://bing.com for search"
        expected = "Visit [Google](https://google.com) or  for search"
        assert CleanProcessor.clean(text, process_rule) == expected

        text = "Image ![alt](https://img.com/pic.jpg) and link https://example.com"
        expected = "Image ![alt](https://img.com/pic.jpg) and link "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_urls_with_query_parameters(self):
        """Test URL removal with query parameters."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Visit https://example.com?param=value&foo=bar for details"
        expected = "Visit  for details"
        assert CleanProcessor.clean(text, process_rule) == expected

        text = "[Link](https://example.com?param=value) text https://other.com?q=test"
        expected = "[Link](https://example.com?param=value) text "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_urls_with_fragments(self):
        """Test URL removal with fragments."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "See https://example.com#section for more"
        expected = "See  for more"
        assert CleanProcessor.clean(text, process_rule) == expected

        text = "[Link](https://example.com#anchor) and https://test.com#top"
        expected = "[Link](https://example.com#anchor) and "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_multiple_emails_in_text(self):
        """Test removal of multiple email addresses."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Contact alice@example.com or bob@test.org for help"
        expected = "Contact  or  for help"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_email_with_special_characters(self):
        """Test email removal with various valid characters."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Email: user.name+tag@example.co.uk"
        expected = "Email: "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_http_vs_https_urls(self):
        """Test removal of both HTTP and HTTPS URLs."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Visit http://insecure.com and https://secure.com"
        expected = "Visit  and "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_markdown_image_with_alt_text(self):
        """Test markdown image preservation with various alt text."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "![Description of image](https://example.com/image.png)"
        expected = "![Description of image](https://example.com/image.png)"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_consecutive_markdown_links(self):
        """Test consecutive markdown links without spaces."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "[First](https://first.com)[Second](https://second.com)[Third](https://third.com)"
        expected = "[First](https://first.com)[Second](https://second.com)[Third](https://third.com)"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_newlines_with_various_counts(self):
        """Test newline reduction with different counts."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_extra_spaces", "enabled": True}]}}

        text = "Line1\n\n\nLine2"
        expected = "Line1\n\nLine2"
        assert CleanProcessor.clean(text, process_rule) == expected

        text = "Line1\n\n\n\n\n\n\n\nLine2"
        expected = "Line1\n\nLine2"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_mixed_whitespace_characters(self):
        """Test removal of various Unicode whitespace characters."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_extra_spaces", "enabled": True}]}}

        text = "word1\u2000word2"
        expected = "word1 word2"
        assert CleanProcessor.clean(text, process_rule) == expected

        text = "word1\u3000word2"
        expected = "word1 word2"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_tabs_and_spaces(self):
        """Test tab and space normalization."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_extra_spaces", "enabled": True}]}}

        text = "word1\t\t\tword2"
        expected = "word1 word2"
        assert CleanProcessor.clean(text, process_rule) == expected

        text = "word1     word2"
        expected = "word1 word2"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_combination_of_rules_complex(self):
        """Test complex combination of all rules."""
        process_rule = {
            "rules": {
                "pre_processing_rules": [
                    {"id": "remove_extra_spaces", "enabled": True},
                    {"id": "remove_urls_emails", "enabled": True},
                ]
            }
        }

        text = "Contact\n\n\n\n  me@example.com  \n\nat  [Site](https://site.com)  or  https://other.com"
        expected = "Contact\n\n  \n\nat [Site](https://site.com) or "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_url_at_end_of_sentence(self):
        """Test URL removal at sentence boundaries."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Visit our site at https://example.com."
        expected = "Visit our site at ."
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_url_in_parentheses(self):
        """Test URL removal when surrounded by parentheses."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "See documentation (https://docs.example.com) for details"
        expected = "See documentation () for details"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_markdown_link_empty_text(self):
        """Test markdown link with empty link text."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "[](https://example.com)"
        expected = "[](https://example.com)"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_markdown_link_with_numbers(self):
        """Test markdown link text containing numbers."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "[Link 123](https://example.com)"
        expected = "[Link 123](https://example.com)"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_markdown_link_with_special_chars(self):
        """Test markdown link text with special characters."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "[Link: special!](https://example.com)"
        expected = "[Link: special!](https://example.com)"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_url_with_port(self):
        """Test URL removal with port numbers."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Connect to https://example.com:8080 for service"
        expected = "Connect to  for service"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_url_with_username(self):
        """Test URL removal with username in URL."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Access https://user@example.com/path"
        expected = "Access "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_long_url_with_path(self):
        """Test removal of long URLs with paths."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Download from https://example.com/path/to/resource/file.zip today"
        expected = "Download from  today"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_multiple_spaces_between_words(self):
        """Test multiple space reduction between words."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_extra_spaces", "enabled": True}]}}

        text = "word1        word2"
        expected = "word1 word2"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_newlines_at_start(self):
        """Test newlines at the start of text."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_extra_spaces", "enabled": True}]}}

        text = "\n\n\n\nContent"
        expected = "\n\nContent"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_newlines_at_end(self):
        """Test newlines at the end of text."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_extra_spaces", "enabled": True}]}}

        text = "Content\n\n\n\n"
        expected = "Content\n\n"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_only_newlines(self):
        """Test text containing only newlines."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_extra_spaces", "enabled": True}]}}

        text = "\n\n\n\n\n"
        expected = "\n\n"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_only_spaces(self):
        """Test text containing only spaces."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_extra_spaces", "enabled": True}]}}

        text = "          "
        expected = " "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_email_in_sentence(self):
        """Test email removal within a sentence."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Please contact john.doe@company.com for assistance."
        expected = "Please contact  for assistance."
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_multiple_urls_consecutive(self):
        """Test multiple consecutive URLs."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Links: https://one.com https://two.com https://three.com"
        expected = "Links:   "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_url_with_hyphen_in_domain(self):
        """Test URL with hyphens in domain name."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Visit https://my-example-site.com today"
        expected = "Visit  today"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_url_with_subdomain(self):
        """Test URL with subdomains."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Go to https://api.staging.example.com/endpoint"
        expected = "Go to "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_markdown_image_without_alt(self):
        """Test markdown image without alt text."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "![](https://example.com/image.png)"
        expected = "![](https://example.com/image.png)"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_markdown_nested_in_text(self):
        """Test markdown links nested within larger text blocks."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Before [link](https://example.com) middle https://other.com after"
        expected = "Before [link](https://example.com) middle  after"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_invalid_symbols_with_text(self):
        """Test invalid symbol removal mixed with normal text."""
        text = "Normal<|text|>with\x00invalid\x1fchars"
        expected = "Normal<text>withinvalidchars"
        assert CleanProcessor.clean(text, None) == expected

    def test_clean_unicode_fffe_multiple(self):
        """Test multiple U+FFFE character removal."""
        text = "text\ufffemore\ufffedata\ufffe"
        expected = "textmoredata"
        assert CleanProcessor.clean(text, None) == expected

    def test_clean_all_control_characters(self):
        """Test removal of various control characters."""
        text = "text\x00\x01\x02\x03\x04\x05\x06\x07end"
        expected = "textend"
        assert CleanProcessor.clean(text, None) == expected

    def test_clean_combined_invalid_symbols(self):
        """Test combination of different invalid symbols."""
        text = "<|test|>\x00content\ufffe<|more|>"
        expected = "<test>content<more>"
        assert CleanProcessor.clean(text, None) == expected

    def test_clean_markdown_link_and_image_together(self):
        """Test markdown link followed by markdown image."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "[Link](https://link.com) ![Image](https://image.com/pic.jpg)"
        expected = "[Link](https://link.com) ![Image](https://image.com/pic.jpg)"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_email_with_numbers(self):
        """Test email with numbers in address."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Contact user123@example456.com"
        expected = "Contact "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_url_ending_with_slash(self):
        """Test URL that ends with a slash."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Visit https://example.com/ for info"
        expected = "Visit  for info"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_url_with_encoded_characters(self):
        """Test URL with percent-encoded characters."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Search https://example.com/search?q=hello%20world"
        expected = "Search "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_markdown_link_with_title(self):
        """Test markdown link (title attribute not in URL part)."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "[Link text](https://example.com)"
        expected = "[Link text](https://example.com)"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_spaces_with_newlines_mixed(self):
        """Test mixed spaces and newlines normalization."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_extra_spaces", "enabled": True}]}}

        text = "Line1\n\n\n  \n\n  Line2"
        expected = "Line1\n\n \n\n Line2"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_real_world_text_example_1(self):
        """Test real-world text example with multiple elements."""
        process_rule = {
            "rules": {
                "pre_processing_rules": [
                    {"id": "remove_extra_spaces", "enabled": True},
                    {"id": "remove_urls_emails", "enabled": True},
                ]
            }
        }

        text = """
        For more information, visit [our website](https://example.com) or
        email us at support@example.com.


        You can also check https://blog.example.com for updates.
        """
        expected = """
        For more information, visit [our website](https://example.com) or
        email us at .

        You can also check  for updates.
        """
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_real_world_text_example_2(self):
        """Test another real-world scenario."""
        process_rule = {
            "rules": {
                "pre_processing_rules": [
                    {"id": "remove_extra_spaces", "enabled": True},
                    {"id": "remove_urls_emails", "enabled": True},
                ]
            }
        }

        text = "Contact:  john@company.com    or   visit   https://company.com"
        expected = "Contact:  or visit "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_markdown_with_inline_code(self):
        """Test markdown links alongside inline code (not affected)."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Use [docs](https://docs.com) or see `https://example.com`"
        expected = "Use [docs](https://docs.com) or see ``"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_line_breaks_preservation(self):
        """Test that single and double line breaks are preserved correctly."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_extra_spaces", "enabled": True}]}}

        text = "Line1\nLine2\n\nLine3"
        expected = "Line1\nLine2\n\nLine3"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_url_followed_by_punctuation(self):
        """Test URL followed immediately by punctuation."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Visit https://example.com, https://other.com; or https://third.com!"
        expected = "Visit , ; or !"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_email_followed_by_punctuation(self):
        """Test email followed immediately by punctuation."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Contact user@example.com, admin@test.com; or support@help.com."
        expected = "Contact , ; or ."
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_multiple_markdown_images(self):
        """Test multiple markdown images in sequence."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "![img1](https://a.com/1.jpg) ![img2](https://b.com/2.jpg) ![img3](https://c.com/3.jpg)"
        expected = "![img1](https://a.com/1.jpg) ![img2](https://b.com/2.jpg) ![img3](https://c.com/3.jpg)"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_form_feed_and_carriage_return(self):
        """Test form feed and carriage return handling."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_extra_spaces", "enabled": True}]}}

        text = "word1\f\f\rword2"
        expected = "word1 word2"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_non_breaking_space(self):
        """Test non-breaking space handling."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_extra_spaces", "enabled": True}]}}

        text = "word1\u00a0\u00a0word2"
        expected = "word1 word2"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_ideographic_space(self):
        """Test ideographic space (U+3000) handling."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_extra_spaces", "enabled": True}]}}

        text = "word1\u3000\u3000\u3000word2"
        expected = "word1 word2"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_url_with_tld_variations(self):
        """Test URL removal with various TLDs."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Visit https://example.co.uk or https://site.io or https://page.dev"
        expected = "Visit  or  or "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_markdown_link_multiline(self):
        """Test markdown links across lines."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "[Link](https://example.com)\nNext line"
        expected = "[Link](https://example.com)\nNext line"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_email_at_start_of_text(self):
        """Test email at the very beginning of text."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "user@example.com is the contact"
        expected = " is the contact"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_url_at_start_of_text(self):
        """Test URL at the very beginning of text."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "https://example.com is the website"
        expected = " is the website"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_mixed_newlines_and_content(self):
        """Test complex mix of newlines and content."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_extra_spaces", "enabled": True}]}}

        text = "Para1\n\n\nPara2\n\n\n\nPara3"
        expected = "Para1\n\nPara2\n\nPara3"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_whitespace_only_lines(self):
        """Test lines containing only whitespace."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_extra_spaces", "enabled": True}]}}

        text = "Line1\n   \n   \nLine2"
        expected = "Line1\n \n \nLine2"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_url_in_quotes(self):
        """Test URL within quotes."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = 'Visit "https://example.com" for more'
        expected = 'Visit "" for more'
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_email_in_quotes(self):
        """Test email within quotes."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = 'Email "contact@example.com" for help'
        expected = 'Email "" for help'
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_markdown_link_in_list(self):
        """Test markdown links in list format."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "- [Link1](https://one.com)\n- [Link2](https://two.com)"
        expected = "- [Link1](https://one.com)\n- [Link2](https://two.com)"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_url_with_authentication(self):
        """Test URL with username:password format."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Access https://user:pass@example.com/resource"
        expected = "Access "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_multiple_control_chars_consecutive(self):
        """Test consecutive control characters."""
        text = "text\x00\x01\x02\x03\x04more"
        expected = "textmore"
        assert CleanProcessor.clean(text, None) == expected

    def test_clean_special_bracket_sequences(self):
        """Test special bracket replacement patterns."""
        text = "test<|bracket|>end"
        expected = "test<bracket>end"
        assert CleanProcessor.clean(text, None) == expected

    def test_clean_repeated_invalid_patterns(self):
        """Test repeated invalid symbol patterns."""
        text = "<|<|<|test|>|>|>"
        expected = "<<<test>>>"
        assert CleanProcessor.clean(text, None) == expected

    def test_clean_email_with_subdomain(self):
        """Test email with subdomain in domain part."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Contact user@mail.example.com"
        expected = "Contact "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_url_with_multiple_query_params(self):
        """Test URL with multiple query parameters."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Search https://example.com?q=test&page=1&sort=desc"
        expected = "Search "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_markdown_image_with_title(self):
        """Test markdown image (title not in main pattern)."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "![alt text](https://example.com/img.png)"
        expected = "![alt text](https://example.com/img.png)"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_complex_whitespace_pattern(self):
        """Test complex whitespace pattern."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_extra_spaces", "enabled": True}]}}

        text = "word1\t \t \tword2"
        expected = "word1 word2"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_newline_after_url(self):
        """Test newline immediately after URL."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Visit https://example.com\nfor more info"
        expected = "Visit \nfor more info"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_newline_after_email(self):
        """Test newline immediately after email."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Contact admin@example.com\nfor support"
        expected = "Contact \nfor support"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_markdown_link_with_dash_in_text(self):
        """Test markdown link with dashes in link text."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "[My-Link-Text](https://example.com)"
        expected = "[My-Link-Text](https://example.com)"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_markdown_link_with_underscore(self):
        """Test markdown link with underscores in text."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "[Link_With_Underscores](https://example.com)"
        expected = "[Link_With_Underscores](https://example.com)"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_url_localhost(self):
        """Test localhost URL removal."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Test at http://localhost:3000/api"
        expected = "Test at "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_url_ip_address(self):
        """Test IP address URL removal."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Connect to http://192.168.1.1:8080"
        expected = "Connect to "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_file_protocol_url(self):
        """Test that file:// protocol is not removed (only http/https)."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Open file://path/to/file.txt"
        expected = "Open file://path/to/file.txt"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_ftp_protocol_url(self):
        """Test that ftp:// protocol is not removed (only http/https)."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Download from ftp://ftp.example.com/file"
        expected = "Download from ftp://ftp.example.com/file"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_mixed_valid_invalid_symbols(self):
        """Test mixture of valid and invalid symbols."""
        text = "Normal<|text with|>valid and\x00invalid"
        expected = "Normal<text with>valid and invalid"
        assert CleanProcessor.clean(text, None) == expected

    def test_clean_unicode_replacement_char(self):
        """Test U+FFFE Unicode replacement character removal."""
        text = "start\ufffeend"
        expected = "startend"
        assert CleanProcessor.clean(text, None) == expected

    def test_clean_text_with_emoji_preserved(self):
        """Test that emoji characters are preserved."""
        text = "Hello 😀 World 🌍"
        expected = "Hello 😀 World 🌍"
        assert CleanProcessor.clean(text, None) == expected

    def test_clean_chinese_characters_preserved(self):
        """Test that Chinese characters are preserved."""
        text = "你好世界"
        expected = "你好世界"
        assert CleanProcessor.clean(text, None) == expected

    def test_clean_arabic_characters_preserved(self):
        """Test that Arabic characters are preserved."""
        text = "مرحبا بالعالم"
        expected = "مرحبا بالعالم"
        assert CleanProcessor.clean(text, None) == expected

    def test_clean_cyrillic_characters_preserved(self):
        """Test that Cyrillic characters are preserved."""
        text = "Привет мир"
        expected = "Привет мир"
        assert CleanProcessor.clean(text, None) == expected

    def test_clean_mixed_languages(self):
        """Test mixed language content."""
        text = "Hello 你好 مرحبا Привет"
        expected = "Hello 你好 مرحبا Привет"
        assert CleanProcessor.clean(text, None) == expected

    def test_clean_url_with_hash_in_query(self):
        """Test URL with hash in query parameter."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Visit https://example.com?id=123#section"
        expected = "Visit "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_email_with_dots_in_local_part(self):
        """Test email with multiple dots in local part."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Contact first.middle.last@example.com"
        expected = "Contact "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_url_data_uri(self):
        """Test that data: URI is not removed (only http/https)."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Image data:image/png;base64,ABC123"
        expected = "Image data:image/png;base64,ABC123"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_markdown_reference_link(self):
        """Test standard markdown link (reference style not tested as not in pattern)."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "[Link][1]\n\n[1]: https://example.com"
        expected = "[Link][1]\n\n[1]: "
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_url_with_equals_in_fragment(self):
        """Test URL with equals sign in fragment."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Link https://example.com#key=value here"
        expected = "Link  here"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_multiple_at_symbols(self):
        """Test text with multiple @ symbols (not email)."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Mention @user @another in text"
        expected = "Mention @user @another in text"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_url_without_protocol_not_removed(self):
        """Test that URLs without protocol are not removed."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Visit example.com or www.example.com"
        expected = "Visit example.com or www.example.com"
        assert CleanProcessor.clean(text, process_rule) == expected

    def test_clean_partial_email_not_removed(self):
        """Test that partial email patterns are not removed."""
        process_rule = {"rules": {"pre_processing_rules": [{"id": "remove_urls_emails", "enabled": True}]}}

        text = "Username is user@ or @domain"
        expected = "Username is user@ or @domain"
        assert CleanProcessor.clean(text, process_rule) == expected
