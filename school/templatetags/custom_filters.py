from django import template
 
register = template.Library()
 
@register.filter(name='custom_comma')
def custom_comma(value):
    """Format the number as xx,xx,xxx (comma after every 3 digits and 2 digits)."""
    try:
        value = int(value)
        value_str = str(value)
       
        # Start formatting by adding a comma every 3 digits
        if len(value_str) > 3:
            first_part = value_str[:-3]
            second_part = value_str[-3:]
            first_part_reversed = first_part[::-1]
            formatted_first_part = ",".join([first_part_reversed[i:i+2] for i in range(0, len(first_part_reversed), 2)])[::-1]
            return f"{formatted_first_part},{second_part}"
        else:
            return value_str
    except (ValueError, TypeError):
        return value  # Return the original value in case of error