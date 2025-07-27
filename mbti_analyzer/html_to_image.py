"""
改进的 HTML 转图片功能
使用 Playwright 将 HTML 报告转换为图片，确保资源安全释放
"""

import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from common.exceptions import ResourceCleanupError
from playwright.async_api import async_playwright


class HTMLToImageConverter:
    """HTML 转图片转换器（改进版）"""

    def __init__(self):
        """初始化转换器"""
        self.images_dir = os.path.join(os.path.dirname(__file__), "images")
        os.makedirs(self.images_dir, exist_ok=True)
        self._browser = None
        self._playwright = None

    @asynccontextmanager
    async def _get_browser(self):
        """
        获取浏览器实例的上下文管理器
        确保浏览器资源被正确释放
        """
        browser = None
        playwright = None
        try:
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",  # 避免 /dev/shm 空间不足
                    "--disable-gpu",  # 在某些环境下提高稳定性
                ]
            )
            yield browser
        except Exception as e:
            raise ResourceCleanupError(f"无法启动浏览器: {str(e)}")
        finally:
            # 确保资源被释放
            if browser:
                try:
                    await browser.close()
                except Exception:
                    pass
            if playwright:
                try:
                    await playwright.stop()
                except Exception:
                    pass

    async def convert_async(self, html_path: str, output_path: Optional[str] = None) -> str:
        """
        异步转换 HTML 到图片
        
        Args:
            html_path: HTML 文件路径
            output_path: 输出图片路径（可选）
            
        Returns:
            生成的图片路径
            
        Raises:
            FileNotFoundError: HTML 文件不存在
            ResourceCleanupError: 浏览器操作失败
        """
        # 确保 HTML 文件存在
        if not os.path.exists(html_path):
            raise FileNotFoundError(f"HTML 文件不存在: {html_path}")

        # 生成输出路径
        if output_path is None:
            html_name = Path(html_path).stem
            output_path = os.path.join(self.images_dir, f"{html_name}.png")

        # 使用上下文管理器确保资源释放
        async with self._get_browser() as browser:
            context = None
            page = None
            try:
                # 创建浏览器上下文
                context = await browser.new_context(
                    viewport={"width": 900, "height": 800},
                    device_scale_factor=2,  # 提高截图质量
                    ignore_https_errors=True,  # 忽略本地文件的 HTTPS 错误
                )

                # 创建新页面
                page = await context.new_page()

                # 设置超时
                page.set_default_timeout(30000)  # 30 秒

                # 加载 HTML 文件
                file_url = f"file://{os.path.abspath(html_path)}"
                await page.goto(file_url, wait_until="networkidle")

                # 等待内容加载完成
                try:
                    await page.wait_for_selector(".terminal-body", timeout=5000)
                except Exception:
                    # 如果没有 terminal-body，尝试等待 body
                    await page.wait_for_selector("body", timeout=5000)

                # 获取内容实际高度
                terminal_height = await page.evaluate(
                    """() => {
                    const terminal = document.querySelector('.terminal');
                    const body = document.body;
                    const height = terminal ? terminal.scrollHeight : body.scrollHeight;
                    return Math.min(height + 40, 2000);  // 限制最大高度
                }"""
                )

                # 调整视口高度以适应内容
                await page.set_viewport_size({"width": 900, "height": terminal_height})

                # 稍等一下确保渲染完成
                await page.wait_for_timeout(500)

                # 截图整个页面
                await page.screenshot(
                    path=output_path,
                    full_page=True,
                    type="png",
                    animations="disabled"  # 禁用动画以获得稳定截图
                )

                return output_path

            except asyncio.TimeoutError:
                raise ResourceCleanupError("页面加载超时")
            except Exception as e:
                raise ResourceCleanupError(f"截图失败: {str(e)}")
            finally:
                # 确保页面和上下文被关闭
                if page:
                    try:
                        await page.close()
                    except Exception:
                        pass
                if context:
                    try:
                        await context.close()
                    except Exception:
                        pass

    def convert(self, html_path: str, output_path: Optional[str] = None) -> str:
        """
        同步接口：转换 HTML 到图片
        
        Args:
            html_path: HTML 文件路径
            output_path: 输出图片路径（可选）
            
        Returns:
            生成的图片路径
        """
        # 检查是否已经在事件循环中
        try:
            loop = asyncio.get_running_loop()
            # 如果已经在事件循环中，创建任务
            return asyncio.create_task(self.convert_async(html_path, output_path))
        except RuntimeError:
            # 如果不在事件循环中，创建新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.convert_async(html_path, output_path))
            finally:
                # 清理事件循环
                try:
                    loop.close()
                except Exception:
                    pass


# 保持向后兼容的全局函数
def convert_html_to_image(html_path: str, output_path: Optional[str] = None) -> str:
    """
    便捷函数：转换 HTML 到图片（改进版）
    
    Args:
        html_path: HTML 文件路径
        output_path: 输出图片路径（可选）
        
    Returns:
        生成的图片路径
    """
    converter = HTMLToImageConverter()
    return converter.convert(html_path, output_path)


# 命令行接口
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("使用方法: python html_to_image_safe.py <html_file> [output_image]")
        sys.exit(1)

    html_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        print(f"正在转换 {html_file} 到图片...")
        image_path = convert_html_to_image(html_file, output_file)
        print(f"✓ 图片已生成: {image_path}")
    except FileNotFoundError as e:
        print(f"✗ 文件不存在: {e}")
        sys.exit(1)
    except ResourceCleanupError as e:
        print(f"✗ 转换失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ 未知错误: {e}")
        sys.exit(1)