"""
Common utilities and shared functionality
"""

# 导入所有子模块的功能
from .data import *  # noqa: F401, F403
from .logging import *  # noqa: F401, F403
from .utils import *  # noqa: F401, F403
from .validation import *  # noqa: F401, F403

# 为了向后兼容，重新导出各个子模块中的功能
from .utils.calculations import *  # noqa: F401, F403
from .utils.path_utils import *  # noqa: F401, F403
from .utils.rate_limiter import *  # noqa: F401, F403
from .data.tweet_utils import *  # noqa: F401, F403
from .validation.exceptions import *  # noqa: F401, F403
from .validation.validators import *  # noqa: F401, F403
from .logging.logger import *  # noqa: F401, F403

# 创建模块级别的导入兼容性
import sys

# 导入实际的子模块
from .utils import calculations
from .utils import path_utils
from .utils import rate_limiter
from .data import tweet_utils
from .validation import exceptions
from .validation import validators
from .logging import logger

# 注册模块别名，使得旧的导入路径继续工作
sys.modules['common.calculations'] = calculations
sys.modules['common.path_utils'] = path_utils
sys.modules['common.rate_limiter'] = rate_limiter
sys.modules['common.tweet_utils'] = tweet_utils
sys.modules['common.exceptions'] = exceptions
sys.modules['common.validators'] = validators
sys.modules['common.logger'] = logger