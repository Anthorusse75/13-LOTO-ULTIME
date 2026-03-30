import LoadingSpinner from "@/components/common/LoadingSpinner";
import { useGraph } from "@/hooks/useStatistics";
import * as d3 from "d3";
import { useEffect, useMemo, useRef } from "react";

export default function GraphTab() {
  const { data: graph, isLoading } = useGraph();
  const svgRef = useRef<SVGSVGElement>(null);

  const communityColors = useMemo(
    () => d3.scaleOrdinal(d3.schemeTableau10),
    [],
  );

  useEffect(() => {
    if (!graph || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const width = svgRef.current.clientWidth;
    const height = 500;

    svg.attr("viewBox", `0 0 ${width} ${height}`);

    // Build nodes and links from graph data
    const nodes = graph.centrality.map((c) => ({
      id: c.number,
      degree: c.degree,
      betweenness: c.betweenness,
      community: c.community,
    }));

    // Use top cooccurrence pairs as edges (from centrality data, link within same community)
    const links: { source: number; target: number }[] = [];
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        if (nodes[i].community === nodes[j].community) {
          links.push({ source: nodes[i].id, target: nodes[j].id });
        }
      }
    }

    const simulation = d3
      .forceSimulation(nodes as d3.SimulationNodeDatum[])
      .force(
        "link",
        d3
          .forceLink(links)
          .id((d: d3.SimulationNodeDatum) => (d as { id: number }).id)
          .distance(60),
      )
      .force("charge", d3.forceManyBody().strength(-100))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const g = svg.append("g");

    // Zoom
    svg.call(
      d3
        .zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.3, 5])
        .on("zoom", (event) => {
          g.attr("transform", event.transform);
        }),
    );

    // Links
    const link = g
      .append("g")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke", "var(--color-border)")
      .attr("stroke-opacity", 0.3)
      .attr("stroke-width", 1);

    // Nodes
    const nodeSize = d3
      .scaleLinear()
      .domain(d3.extent(nodes, (d) => d.degree) as [number, number])
      .range([5, 18]);

    const node = g
      .append("g")
      .selectAll("circle")
      .data(nodes)
      .join("circle")
      .attr("r", (d) => nodeSize(d.degree))
      .attr("fill", (d) => communityColors(String(d.community)))
      .attr("stroke", "var(--color-background)")
      .attr("stroke-width", 1.5)
      .call(
        d3
          .drag<SVGCircleElement, (typeof nodes)[0]>()
          .on(
            "start",
            (
              event: d3.D3DragEvent<
                SVGCircleElement,
                (typeof nodes)[0],
                unknown
              >,
              d,
            ) => {
              if (!event.active) simulation.alphaTarget(0.3).restart();
              (d as d3.SimulationNodeDatum).fx = (
                d as d3.SimulationNodeDatum
              ).x;
              (d as d3.SimulationNodeDatum).fy = (
                d as d3.SimulationNodeDatum
              ).y;
            },
          )
          .on(
            "drag",
            (
              event: d3.D3DragEvent<
                SVGCircleElement,
                (typeof nodes)[0],
                unknown
              >,
              d,
            ) => {
              (d as d3.SimulationNodeDatum).fx = event.x;
              (d as d3.SimulationNodeDatum).fy = event.y;
            },
          )
          .on(
            "end",
            (
              event: d3.D3DragEvent<
                SVGCircleElement,
                (typeof nodes)[0],
                unknown
              >,
              d,
            ) => {
              if (!event.active) simulation.alphaTarget(0);
              (d as d3.SimulationNodeDatum).fx = null;
              (d as d3.SimulationNodeDatum).fy = null;
            },
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          ) as any,
      );

    // Labels
    const labels = g
      .append("g")
      .selectAll("text")
      .data(nodes)
      .join("text")
      .text((d) => String(d.id))
      .attr("font-size", "10px")
      .attr("fill", "var(--color-text-primary)")
      .attr("text-anchor", "middle")
      .attr("dy", "0.35em")
      .attr("font-family", "JetBrains Mono, monospace")
      .style("pointer-events", "none");

    simulation.on("tick", () => {
      link
        .attr(
          "x1",
          (d: Record<string, unknown>) => (d.source as { x: number }).x,
        )
        .attr(
          "y1",
          (d: Record<string, unknown>) => (d.source as { y: number }).y,
        )
        .attr(
          "x2",
          (d: Record<string, unknown>) => (d.target as { x: number }).x,
        )
        .attr(
          "y2",
          (d: Record<string, unknown>) => (d.target as { y: number }).y,
        );

      node
        .attr("cx", (d) => (d as d3.SimulationNodeDatum).x!)
        .attr("cy", (d) => (d as d3.SimulationNodeDatum).y!);

      labels
        .attr("x", (d) => (d as d3.SimulationNodeDatum).x!)
        .attr("y", (d) => (d as d3.SimulationNodeDatum).y!);
    });

    return () => {
      simulation.stop();
    };
  }, [graph, communityColors]);

  if (isLoading) return <LoadingSpinner />;
  if (!graph)
    return (
      <p className="text-text-secondary">Aucune donnée de graphe disponible.</p>
    );

  return (
    <div className="space-y-6">
      {/* Graph visualization */}
      <div className="bg-surface rounded-lg border border-border p-4">
        <h3 className="text-sm font-semibold mb-3">
          Graphe de réseau — Communautés
        </h3>
        <svg ref={svgRef} className="w-full" style={{ height: 500 }} />
        <p className="text-xs text-text-secondary mt-2">
          Réseau de co-occurrence : chaque couleur représente une communauté
          détectée, la taille des nœuds reflète la centralité.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-surface rounded-lg border border-border p-4">
          <p className="text-xs text-text-secondary">Communautés</p>
          <p className="font-mono text-lg">{graph.communities.length}</p>
        </div>
        <div className="bg-surface rounded-lg border border-border p-4">
          <p className="text-xs text-text-secondary">Densité</p>
          <p className="font-mono text-lg">{graph.density.toFixed(4)}</p>
        </div>
        <div className="bg-surface rounded-lg border border-border p-4">
          <p className="text-xs text-text-secondary">Coef. clustering</p>
          <p className="font-mono text-lg">
            {graph.clustering_coefficient.toFixed(4)}
          </p>
        </div>
        <div className="bg-surface rounded-lg border border-border p-4">
          <p className="text-xs text-text-secondary">Nœuds</p>
          <p className="font-mono text-lg">{graph.centrality.length}</p>
        </div>
      </div>

      {/* Communities */}
      <div className="bg-surface rounded-lg border border-border p-4">
        <h3 className="text-sm font-semibold mb-3">Communautés détectées</h3>
        <div className="space-y-2">
          {graph.communities.map((community, i) => (
            <div key={i} className="flex items-center gap-2 text-sm">
              <span
                className="w-3 h-3 rounded-full flex-shrink-0"
                style={{
                  background: d3.schemeTableau10[i % 10],
                }}
              />
              <span className="text-text-secondary">Communauté {i + 1}:</span>
              <span className="font-mono">
                {community.sort((a, b) => a - b).join(", ")}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
