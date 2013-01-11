
#ifndef DIALS_GEOMETRY_TRANSFORM_FROM_DETECTOR_TO_XDS_H
#define DIALS_GEOMETRY_TRANSFORM_FROM_DETECTOR_TO_XDS_H

#include "from_detector_to_beam_vector.h"
#include "from_beam_vector_to_xds.h"

namespace dials { namespace geometry { namespace transform {

/** A transform from detector coordinates to XDS coordinates */
class FromDetectorToXds {

public:

    /** Default constructor */
    FromDetectorToXds() {}

    /**
     * Initialise the transform using component transform objects.
     * @param xy_to_s1 The detector to beam vector transform
     * @param s1_to_xds The beam vector to XDS transform
     */
    FromDetectorToXds(FromDetectorToBeamVector xy_to_s1,
                      FromBeamVectorToXds s1_to_xds,
                      double wavelength)
        : _xy_to_s1(xy_to_s1),
          _s1_to_xds(s1_to_xds),
          _wavelength_r(1.0 / wavelength) {}
    
    /**
     * Initialise the transform with all the stuff that's needed for the
     * component transforms
     * @param dcs The detector coordinate system
     * @param origin The origin of the detector coordinate system
     * @param distance The distance from the detector to the crystal
     * @param xcs The XDS coordinate system
     * @param s1 The diffracted beam vector
     * @param phi The rotation angle
     */
    FromDetectorToXds(DetectorCoordinateSystem dcs,
                      scitbx::vec2 <double> origin,
                      double distance,
                      XdsCoordinateSystem xcs,
                      scitbx::vec3 <double> s1,
                      double phi,
                      double wavelength)
        : _xy_to_s1(dcs, origin, distance),
          _s1_to_xds(xcs, s1, phi),
          _wavelength_r(1.0 / wavelength) {}
     
public:

    /**
     * Apply the transform to a detector coordinate at a given rotation angle
     * @param xy The detector coordinate
     * @param phi The rotation angle
     * @returns The XDS coordinate
     */
    scitbx::vec3 <double> apply(scitbx::vec2 <double> xy, double phi_dash) {
        return _s1_to_xds.apply(_xy_to_s1.apply(xy).normalize() * _wavelength_r, 
                                phi_dash);
    }

private:

    FromDetectorToBeamVector _xy_to_s1;
    FromBeamVectorToXds _s1_to_xds;
    double _wavelength_r;
};

}}} // namespace = dials::geometry::transform

#endif // DIALS_GEOMETRY_TRANSFORM_FROM_DETECTOR_TO_XDS_H
