"""
Created by Epic at 10/17/20
"""
from main import Bot

from discord.ext.commands import Cog
from aiohttp.web import Application, RouteTableDef, Request, Response, _run_app


class Analytics(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.metrics = {}
        self.app = Application()
        self.routes = RouteTableDef()

        self.metrics["queue_size"] = {"help": "Simp for maize", "type": "gauge", "value": 1.0}

        self.routes.get("/metrics")(self.get_metrics)

        self.app.add_routes(self.routes)
        self.bot.loop.create_task(self.start())

    async def start(self):
        await _run_app(self.app, port=8080)

    def format_response(self):
        response = ""
        for metric_name, metric_data in self.metrics.items():
            response += f"# HELP {metric_name} {metric_data['help']}\n"
            response += f"# TYPE {metric_name} {metric_data['type']}\n"
            response += f"{metric_name} {metric_data['value']}\n"
        return response

    async def get_metrics(self, request: Request):
        return Response(body=self.format_response())

    def update_metric(self, name, value, description):
        if self.metrics.get(name, None) is None:
            self.metrics[name] = {
                "type": "gauge",
                "description": description,
                "value": 0
            }
        self.metrics[name]["value"] = value


def setup(bot: Bot):
    bot.add_cog(Analytics(bot))
