#!/usr/bin/env python3
"""
Address Map Generator for Verilog Modules
Parses Verilog files to extract BASEADDR and HIGHADDR parameters from module instantiations
and generates a formatted address map.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ModuleInstance:
    """Represents an instantiated module with address information"""
    module_name: str
    instance_name: str
    baseaddr: str
    highaddr: str
    baseaddr_value: Optional[int] = None
    highaddr_value: Optional[int] = None


class AddressMapGenerator:
    """Parses Verilog files and generates address maps"""
    
    def __init__(self):
        self.parameters: Dict[str, str] = {}
        self.modules: List[ModuleInstance] = []
        self.evaluated_params: Dict[str, int] = {}
    
    def parse_verilog_file(self, filepath: Path) -> None:
        """Parse a Verilog file for localparams and module instantiations"""
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Extract localparams (parameter definitions)
        localparam_pattern = r'localparam\s+(\w+)\s*=\s*([^;]+);'
        for match in re.finditer(localparam_pattern, content):
            param_name = match.group(1)
            param_value = match.group(2).strip()
            self.parameters[param_name] = param_value
        
        # Extract module instantiations with BASEADDR/HIGHADDR
        # This pattern captures module name, instance name, and parameters
        instance_pattern = r'(\w+)\s*#\s*\(\s*(.*?)\s*\)\s+(\w+)\s*\('
        
        for match in re.finditer(instance_pattern, content, re.DOTALL):
            module_name = match.group(1)
            params_block = match.group(2)
            instance_name = match.group(3)
            
            # Extract BASEADDR and HIGHADDR from parameters
            baseaddr_match = re.search(
                r'\.BASEADDR\s*\(\s*(\w+(?:\s*[\+\-]\s*[^\)]+)?)\s*\)',
                params_block
            )
            highaddr_match = re.search(
                r'\.HIGHADDR\s*\(\s*(\w+(?:\s*[\+\-]\s*[^\)]+)?)\s*\)',
                params_block
            )
            
            if baseaddr_match and highaddr_match:
                baseaddr = baseaddr_match.group(1).strip()
                highaddr = highaddr_match.group(1).strip()
                
                modules = ModuleInstance(
                    module_name=module_name,
                    instance_name=instance_name,
                    baseaddr=baseaddr,
                    highaddr=highaddr
                )
                self.modules.append(modules)
    
    def evaluate_parameter(self, param_expr: str) -> Optional[int]:
        """Evaluate a parameter expression (may contain hex/binary literals and arithmetic)"""
        if param_expr in self.evaluated_params:
            return self.evaluated_params[param_expr]
        
        try:
            # Use the raw parameter definition if this expression is a parameter name.
            expr = self.parameters.get(param_expr, param_expr)

            # Replace parameter references with their evaluated integer values.
            for param_name in sorted(self.parameters, key=len, reverse=True):
                if param_name == param_expr:
                    continue
                if re.search(r'\b' + re.escape(param_name) + r'\b', expr):
                    evaluated_value = self.evaluate_parameter(param_name)
                    if evaluated_value is not None:
                        expr = re.sub(r'\b' + re.escape(param_name) + r'\b', str(evaluated_value), expr)

            # Remove whitespace
            expr = re.sub(r'\s+', '', expr)
            
            # Evaluate the expression
            # Support hex (16'hXXXX), binary (8'bXXXX), and decimal
            expr = self._convert_literals(expr)
            result = eval(expr, {"__builtins__": {}})
            
            self.evaluated_params[param_expr] = result
            return result
        except Exception as e:
            print(f"Warning: Could not evaluate '{param_expr}': {e}", file=sys.stderr)
            return None
    
    def _evaluate_value(self, value: str) -> int:
        """Convert a parameter value to an integer"""
        value = value.strip()
        try:
            # Handle hex literals (16'hXXXX)
            hex_match = re.match(r"(\d+)'h([0-9A-Fa-f]+)", value)
            if hex_match:
                return int(hex_match.group(2), 16)
            
            # Handle binary literals (8'bXXXX)
            bin_match = re.match(r"(\d+)'b([01]+)", value)
            if bin_match:
                return int(bin_match.group(2), 2)
            
            # Handle decimal
            if value.isdigit():
                return int(value)
            
            # If it's a parameter reference, try to evaluate it
            if value in self.parameters:
                evaluated_param = self.evaluate_parameter(value)
                return evaluated_param if evaluated_param is not None else 0
            
            return 0
        except Exception as e:
            print(f"Warning: Could not evaluate value '{value}': {e}", file=sys.stderr)
            return 0
    
    def _convert_literals(self, expr: str) -> str:
        """Convert Verilog-style literals to Python-compatible format"""
        # Convert hex literals (16'hXXXX to 0xXXXX)
        expr = re.sub(r"(\d+)'h([0-9A-Fa-f]+)", r"0x\2", expr)
        # Convert binary literals (8'bXXXX to 0bXXXX)
        expr = re.sub(r"(\d+)'b([01]+)", r"0b\2", expr)
        return expr
    
    def evaluate_all_addresses(self) -> None:
        """Evaluate all BASEADDR and HIGHADDR expressions"""
        for module in self.modules:
            module.baseaddr_value = self.evaluate_parameter(module.baseaddr)
            module.highaddr_value = self.evaluate_parameter(module.highaddr)
    
    def check_overlaps(self) -> List[Tuple[ModuleInstance, ModuleInstance, int, int]]:
        """
        Check for address space overlaps between modules.
        
        Returns:
            List of tuples (module1, module2, overlap_start, overlap_end)
        """
        overlaps = []
        
        # Filter modules with valid addresses
        valid_modules = [
            m for m in self.modules
            if m.baseaddr_value is not None and m.highaddr_value is not None
        ]
        
        # Check each pair of modules
        for i, mod1 in enumerate(valid_modules):
            for mod2 in valid_modules[i+1:]:
                # Check if ranges overlap
                if not (mod1.highaddr_value < mod2.baseaddr_value or 
                        mod2.highaddr_value < mod1.baseaddr_value):
                    # Calculate overlap region
                    overlap_start = max(mod1.baseaddr_value, mod2.baseaddr_value)
                    overlap_end = min(mod1.highaddr_value, mod2.highaddr_value)
                    overlaps.append((mod1, mod2, overlap_start, overlap_end))
        
        return overlaps
    
    def generate_map(self) -> str:
        """Generate formatted address map"""
        self.evaluate_all_addresses()
        
        # Sort by base address
        sorted_modules = sorted(
            self.modules,
            key=lambda m: m.baseaddr_value if m.baseaddr_value is not None else 0xFFFFFFFF
        )
        
        # Generate output
        lines = []
        lines.append("=" * 80)
        lines.append("ADDRESS MAP - Module Instance Addresses".center(80))
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"{'Module':<20} {'Instance':<20} {'Base Address':<15} {'High Address':<15}")
        lines.append("-" * 80)
        
        for module in sorted_modules:
            if module.baseaddr_value is not None and module.highaddr_value is not None:
                base_str = f"0x{module.baseaddr_value:04X}"
                high_str = f"0x{module.highaddr_value:04X}"
                size = module.highaddr_value - module.baseaddr_value + 1
                lines.append(
                    f"{module.module_name:<20} {module.instance_name:<20} "
                    f"{base_str:<15} {high_str:<15} (Size: {size} bytes)"
                )
            else:
                lines.append(
                    f"{module.module_name:<20} {module.instance_name:<20} "
                    f"{module.baseaddr:<15} {module.highaddr:<15}"
                )
        
        lines.append("-" * 80)
        lines.append("")
        
        # Check for overlaps
        overlaps = self.check_overlaps()
        if overlaps:
            lines.append("⚠️  ADDRESS SPACE CONFLICTS DETECTED!")
            lines.append("=" * 80)
            for mod1, mod2, overlap_start, overlap_end in overlaps:
                overlap_size = overlap_end - overlap_start + 1
                lines.append(f"CONFLICT: {mod1.instance_name} <-> {mod2.instance_name}")
                lines.append(f"  {mod1.module_name} ({mod1.instance_name}): "
                           f"0x{mod1.baseaddr_value:04X} - 0x{mod1.highaddr_value:04X}")
                lines.append(f"  {mod2.module_name} ({mod2.instance_name}): "
                           f"0x{mod2.baseaddr_value:04X} - 0x{mod2.highaddr_value:04X}")
                lines.append(f"  Overlap region: 0x{overlap_start:04X} - 0x{overlap_end:04X} "
                           f"({overlap_size} bytes)")
                lines.append("")
            lines.append("=" * 80)
            lines.append("")
        else:
            lines.append("✓ No address space conflicts detected")
            lines.append("")
        
        # Summary of parameters
        if self.parameters:
            lines.append("Parameter Values:")
            lines.append("-" * 80)
            for param_name, param_value in sorted(self.parameters.items()):
                evaluated = self.evaluate_parameter(param_name)
                if evaluated is not None:
                    lines.append(f"  {param_name:<30} = {param_value:<30} (0x{evaluated:04X})")
                else:
                    lines.append(f"  {param_name:<30} = {param_value}")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_csv(self) -> str:
        """Generate address map in CSV format"""
        self.evaluate_all_addresses()
        
        sorted_modules = sorted(
            self.modules,
            key=lambda m: m.baseaddr_value if m.baseaddr_value is not None else 0xFFFFFFFF
        )
        
        lines = ["Module,Instance,Base Address,High Address,Size (bytes)"]
        for module in sorted_modules:
            if module.baseaddr_value is not None and module.highaddr_value is not None:
                size = module.highaddr_value - module.baseaddr_value + 1
                lines.append(
                    f"{module.module_name},{module.instance_name},"
                    f"0x{module.baseaddr_value:04X},0x{module.highaddr_value:04X},{size}"
                )
        
        return "\n".join(lines)
    
    def generate_verilog_header(self) -> str:
        """Generate Verilog header file with address constants"""
        self.evaluate_all_addresses()
        
        sorted_modules = sorted(
            self.modules,
            key=lambda m: m.baseaddr_value if m.baseaddr_value is not None else 0xFFFFFFFF
        )
        
        lines = [
            "// Auto-generated address map header",
            "// This file was generated by generate_address_map.py",
            "",
        ]
        
        for module in sorted_modules:
            if module.baseaddr_value is not None and module.highaddr_value is not None:
                prefix = module.instance_name.upper()
                lines.append(f"// {module.module_name} ({module.instance_name})")
                lines.append(f"`define {prefix}_BASEADDR  16'h{module.baseaddr_value:04X}")
                lines.append(f"`define {prefix}_HIGHADDR  16'h{module.highaddr_value:04X}")
                lines.append("")
        
        return "\n".join(lines)
    
    def generate_conflict_report(self) -> str:
        """Generate a detailed address conflict report"""
        self.evaluate_all_addresses()
        overlaps = self.check_overlaps()
        
        lines = []
        lines.append("=" * 80)
        lines.append("ADDRESS SPACE CONFLICT REPORT".center(80))
        lines.append("=" * 80)
        lines.append("")
        
        if not overlaps:
            lines.append("✓ No conflicts found - all address spaces are properly allocated")
            lines.append("")
        else:
            lines.append(f"⚠️  Found {len(overlaps)} conflict(s)")
            lines.append("")
            
            for idx, (mod1, mod2, overlap_start, overlap_end) in enumerate(overlaps, 1):
                overlap_size = overlap_end - overlap_start + 1
                lines.append(f"Conflict #{idx}")
                lines.append("-" * 80)
                lines.append(f"Module 1: {mod1.module_name}")
                lines.append(f"  Instance:      {mod1.instance_name}")
                lines.append(f"  Address range: 0x{mod1.baseaddr_value:04X} - 0x{mod1.highaddr_value:04X}")
                lines.append(f"  Size:          {mod1.highaddr_value - mod1.baseaddr_value + 1} bytes")
                lines.append("")
                lines.append(f"Module 2: {mod2.module_name}")
                lines.append(f"  Instance:      {mod2.instance_name}")
                lines.append(f"  Address range: 0x{mod2.baseaddr_value:04X} - 0x{mod2.highaddr_value:04X}")
                lines.append(f"  Size:          {mod2.highaddr_value - mod2.baseaddr_value + 1} bytes")
                lines.append("")
                lines.append(f"OVERLAPPING REGION:")
                lines.append(f"  Start address: 0x{overlap_start:04X}")
                lines.append(f"  End address:   0x{overlap_end:04X}")
                lines.append(f"  Overlap size:  {overlap_size} bytes")
                lines.append("")
        
        return "\n".join(lines)


def main():
    """Main entry point"""
    # Find Verilog files in current directory and subdirectories
    verilog_files = list(Path(".").glob("**/*.v"))
    
    if not verilog_files:
        print("No Verilog files found in current directory", file=sys.stderr)
        sys.exit(1)
    
    generator = AddressMapGenerator()
    
    # Parse all Verilog files
    for vfile in verilog_files:
        print(f"Parsing {vfile}...", file=sys.stderr)
        generator.parse_verilog_file(vfile)
    
    # Generate output formats
    print("\n" + generator.generate_map())
    
    # Save to files
    csv_path = Path("address_map.csv")
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write(generator.generate_csv())
    print(f"CSV address map saved to: {csv_path}")
    
    vh_path = Path("address_map.vh")
    with open(vh_path, 'w', encoding='utf-8') as f:
        f.write(generator.generate_verilog_header())
    print(f"Verilog header saved to: {vh_path}")
    
    # Generate and save conflict report
    conflict_report = generator.generate_conflict_report()
    print("\n" + conflict_report)
    
    conflicts_path = Path("address_conflicts.txt")
    with open(conflicts_path, 'w', encoding='utf-8') as f:
        f.write(conflict_report)
    print(f"Conflict report saved to: {conflicts_path}")
    
    # Exit with error code if conflicts found
    if generator.check_overlaps():
        sys.exit(1)


if __name__ == "__main__":
    main()
